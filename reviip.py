# written by a very intoxicated lovelace on 5/27/2025
# finished by a slightly less intoxicated lovelace on 8/31/2025
# thanks ken <3

import os
import requests
from urllib.parse import urlparse, parse_qs
from PIL import Image
from natsort import natsorted

print("please zoom into the image fully, then grab the url of a tile through inspect element or other means")
url = input("paste the url here: ")

parsedUrl = urlparse(url)
queryParams = parse_qs(parsedUrl.query)
jtlZoomVal = queryParams.get('JTL', [''])[0].split(',')[0]

# download all of the frames

urlBase = url.split("JTL=")[0]

imageName = os.path.basename(queryParams.get('FIF', [''])[0])
scriptDir = os.path.dirname(os.path.abspath(__file__))
folderPath = os.path.join(scriptDir, imageName)
stageTwo = os.path.join(folderPath, "rows")

os.makedirs(folderPath, exist_ok=True)
os.makedirs(stageTwo, exist_ok=True)

def downloadImageFrames():
    i = 0
    response = None
    
    while not hasattr(response, "status_code") or response.status_code == 200:
        filePath = os.path.join(folderPath, str(i))

        if os.path.exists(filePath):
            print(f"skipping already downloaded tile(s), {i}", end='\r')
            i += 1
            continue;

        imgUrl = urlBase + "JTL=" + jtlZoomVal + ',' + str(i)

        try:
            response = requests.get(imgUrl)
        except Exception as e:
            print(f"some error occured while downloading tile {i}, retrying...")
            continue
        
        if response.status_code != 200:
            print(f"\nfinished download tiles, {i} total.")
            return i;
    
        print(f"downloaded tile: {i}", end='\r')

        filePath = os.path.join(folderPath, str(i))
    
        with open(filePath, "wb") as f:
            f.write(response.content)
       
            i += 1

totalFrames = downloadImageFrames()

def concatenateVertically(imgs):
    totalHeight = sum(img.height for img in imgs)
    image = Image.new('RGB', (imgs[0].width, totalHeight))

    offset = 0
    for img in imgs:
        image.paste(img, (0, offset))
        offset += img.height

    return image

def concatenateHorizontally(imgs):
    totalWidth = sum(img.width for img in imgs)
    image = Image.new('RGB', (totalWidth, imgs[0].height))

    offset = 0
    for img in imgs:
        image.paste(img, (offset, 0))
        offset += img.width

    return image    
    
# check if frame sizes and concatonate accordinatly (i was really drunk, holy shit)
def concatenateFrames():
    baseWidth = 0 # this should always been 256 but we might as well check
    framesPerRow = 0
    firstImage = True

    files = os.listdir(folderPath)
    
    for f in natsorted(files): # os.listdir(folderPath):
        imagePath = os.path.join(folderPath, f)

        if not os.path.isfile(imagePath):
            continue
        
        with Image.open(imagePath) as img:
            width, height = img.size
            print(f"{int(f)} {width}")
            if firstImage:
                baseWidth = width
                print(f"found tile width: {width}")
                firstImage = False
                continue;
            
            if (width != baseWidth):
                framesPerRow = int(f) + 1
                print(f"found tiles per row: {framesPerRow}")
                break

    rows = int(totalFrames / framesPerRow)

    for i in range(0, rows):
        images = [Image.open(folderPath+f"/{i}") for i in range(framesPerRow * i, framesPerRow * (i + 1))]        
        
        row = concatenateHorizontally(images)
        row.save(stageTwo+f"/{i}.jpg")

        print(f"concatenated row {i} of {rows - 1}.", end='\r')

    columns = [Image.open(stageTwo+f"/{i}.jpg") for i in range(0, rows)]
    image = concatenateVertically(columns)
    image.save(f"{imageName}.jpg")
    
    print(f"\nfinished downloading and recreating image {imageName}.jpg!")

concatenateFrames()
