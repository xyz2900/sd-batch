import os
import sys
from threading import Thread
import requests
import time
import yaml
import base64
import io
import datetime as dt
from PIL import Image, PngImagePlugin

yfiles = sys.argv[1:]
argv = sys.argv[:1]
sys.argv = argv
# --xformers --enable-insecure-extension-access --share --gradio-queue
argv_add = ['--api', '--nowebui', '--xformers', '--enable-insecure-extension-access', '--share', '--gradio-queue']
#argv_add = ['--api', '--nowebui', '--skip-torch-cuda-test', '--upcast-sampling', '--no-half-vae', '--use-cpu', 'interrogate']
sys.argv.extend(argv_add)

from modules import launch_utils

args = launch_utils.args
python = launch_utils.python
git = launch_utils.git
index_url = launch_utils.index_url
dir_repos = launch_utils.dir_repos

commit_hash = launch_utils.commit_hash
git_tag = launch_utils.git_tag

run = launch_utils.run
is_installed = launch_utils.is_installed
repo_dir = launch_utils.repo_dir

run_pip = launch_utils.run_pip
check_run_python = launch_utils.check_run_python
git_clone = launch_utils.git_clone
git_pull_recursive = launch_utils.git_pull_recursive
list_extensions = launch_utils.list_extensions
run_extension_installer = launch_utils.run_extension_installer
prepare_environment = launch_utils.prepare_environment
configure_for_tests = launch_utils.configure_for_tests
start = launch_utils.start

def load_yfile(fname):
   yml = None
   with open(fname) as file:
      try:
         yml = yaml.load(file, Loader=yaml.FullLoader)
      except yaml.YAMLError as exc:
         print(exc)
         yml = None

   return yml

def batchProcess(*args):
   url = 'http://127.0.0.1:7861'
   print("batchProcess:{}".format(args))
   time.sleep(20)
   # API接続完了待ち
   # モデル一覧
   while(1):
      responce = requests.get(f"{url}/sdapi/v1/sd-models")
      if responce.status_code == 200:
         print("waiting ... {}".format(responce.status_code))
         break

      time.sleep(10)
   print("START PROCESS ...")

   #from modules import sd_models
   #sd_models.list_models()
   # checkpoint_aliases = sd_models.checkpoint_aliases
   # モデル一覧
   if responce.status_code == 200:
      sd_models = responce.json()
      sd_models = [model["title"] for model in sd_models]
      for model in sd_models:
         print(model)

   st_time = time.time()
   for arg in args:
      ydata = load_yfile(arg)
      if ydata:
         iname = ydata['text2image'].get('name', 'other') # nameが設定されていない場合はotherにする
         output_dir = ydata['text2image'].get('output_dir', './outputs')

         # モデル変更
         #model = "AnythingV5Ink_v5PrtRE.safetensors [7f96a1a9ac]"
         model = ydata['text2image'].get('sd_model')
         option_payload = {
            "sd_model_checkpoint": model,
            # "CLIP_stop_at_last_layers": 2
         }
         response = requests.post(url=f'{url}/sdapi/v1/options', json=option_payload)
         if response.status_code != 200:
            print(response.status_code, response.reason)
            os._exit(0)
         print("MODEL LOADED: {}".format(model))

         #checkpoint = checkpoint_aliases.get(ydata['text2image'].get('sd_model'), None)
         #sd_models.load_model(checkpoint)

         # txt2img
         # パラメータ設定
         jdata = ydata['text2image']
         jdata.pop('name')
         jdata.pop('sd_model')
         jdata.pop('output_dir')
         if jdata.get('enable_hr') == True:
            if jdata.get('hr_checkpoint_name') == None:
               jdata['hr_checkpoint_name'] = jdata.get('sd_model')
            if jdata.get('hr_sampler_name') == None:
               jdata['hr_sampler_name'] = jdata.get('sampler_name')

         response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=jdata)
         print(response.status_code)
         if response.status_code == 200:
            rdata = response.json()
            simages = rdata['images']
            for simage in simages:
               oimage = Image.open(io.BytesIO(base64.b64decode(simage.split(",", 1)[0])))

               png_payload = {
                  "image": "data:image/png;base64," + simage
               }
               response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
               pnginfo = PngImagePlugin.PngInfo()
               pnginfo.add_text("parameters", response2.json().get("info"))

               odir = f"{output_dir}/{iname}"
               ofile = "{}/{}.png".format(odir, dt.datetime.now().strftime("%Y%m%d%H%M%S%f"))
               print(ofile)
               os.makedirs(odir, exist_ok=True)
               oimage.save(ofile, pnginfo=pnginfo)

   en_time = time.time()
   print("batchProcess: finish total={}sec".format(en_time - st_time))
   os._exit(0)
   return 1

def main():
    if args.dump_sysinfo:
        filename = launch_utils.dump_sysinfo()

        print(f"Sysinfo saved as {filename}. Exiting...")

        exit(0)

    launch_utils.startup_timer.record("initial startup")

    with launch_utils.startup_timer.subcategory("prepare environment"):
        if not args.skip_prepare_environment:
            prepare_environment()

    if args.test_server:
        configure_for_tests()

    p1 = Thread(target=batchProcess, args=(yfiles))
    p1.start()
    #p1.join()
    print(f"Launching {'API server' if '--nowebui' in sys.argv else 'Web UI'} with arguments: {' '.join(sys.argv[1:])}")
    import webui
    webui.api_only()

if __name__ == "__main__":
    main()
