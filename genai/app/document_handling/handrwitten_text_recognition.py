from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

url = "/Users/i_gore/PycharmProjects/study_sync/data/docs/tg_image_1864149188.png"
image = Image.open(url).convert("RGB")
processor = TrOCRProcessor.from_pretrained("fhswf/TrOCR_Math_handwritten")
model = VisionEncoderDecoderModel.from_pretrained("fhswf/TrOCR_Math_handwritten")
pixel_values = processor(images=image, return_tensors="pt").pixel_values
generated_ids = model.generate(pixel_values)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(generated_text)
