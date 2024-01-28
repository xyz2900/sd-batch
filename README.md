# sd-batch
I tried creating a batch program for text-to-image using the API of Stable Diffusion WebUI. It's still in the testing phase.

# install
```
execute install.sh
copy batch_text2image.py and test01.yaml, test02.yaml to stable-diffusion-webui directory
```

# usage
The model to be configured in the YAML file can be obtained by executing the following command without any arguments:

```
python3.10 batch_text2image.py
```
This will display a list of models with their configurations. Please copy the desired model configuration from there.

You can execute the batch program with the following command:

```
cd stable-diffusion-webui
python3.10 batch_text2image.py test01.yaml test02.yaml
```

This command runs the batch_text2image.py program with the specified YAML files (test01.yaml and test02.yaml) as arguments. Make sure that the YAML files contain the necessary configurations for the text-to-image process.


If you specify multiple models in the test03.yaml file as shown below:

```
sd_model: ['beautifulRealistic_v60.safetensors [bc2f30f4ad]', 'beautifulRealistic_v7.safetensors', 'beautifulRealistic_brav5.safetensors']
```
You can process multiple models in bulk using the same prompt. When you execute the batch program with this YAML file, it will perform the text-to-image process using each of the specified models.
