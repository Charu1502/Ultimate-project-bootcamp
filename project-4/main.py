from PIL import Image
import os
import re

def convert_ttb(text,password):
    text += f'###{password}###====END====' # Delimiter for password and end of message
    text = "text:" + text # Prefix to identify start of hidden message
    bi = []
    for i in text:
        bi.append(format(ord(i), '08b')) 
    return ''.join(bi)


def encode(img_path, text, password):
    """Encodes the given text into an image using LSB steganography, with a password for added security.
    The text is first combined with the password and a unique delimiter, then converted to binary.
    Each bit of the binary text is embedded into the least significant bits of the image's pixel values.
    The modified image is saved with a new filename indicating it has been encoded."""
    btext = convert_ttb(text, password) #binary text
    data_index = 0
    img = Image.open(img_path).convert('RGB')
    x, y = img.size
    max_capacity = x * y * 3  # Each pixel can store 3 bits (R, G, B)
    if len(btext) > max_capacity:
        raise ValueError("Text is too long to encode in the given image.")
    pixel = img.load()
    for i in range(x):
        for j in range(y):
            r, g, b = pixel[i,j]
            if data_index < len(btext):
                r = (r & 254) | int(btext[data_index])  #modify LSB of red pixel
                data_index += 1
            if data_index < len(btext):
                g = (g & 254) | int(btext[data_index])  #modify LSB of green pixel
                data_index += 1
            if data_index < len(btext):
                b = (b & 254) | int(btext[data_index])  #modify LSB of blue pixel
                data_index += 1
            pixel[i,j] = (r, g, b)
            if data_index >= len(btext):
                break
        if data_index >= len(btext):
            break
    filename, exp = os.path.splitext(img_path)
    outimg = filename + "_en.png"
    img.save(outimg)

def decode(img_path, password):
    """Decodes hidden text from an image that was encoded using the encode function.
    The function reads the least significant bits of the image's pixel values to reconstruct the binary data.
    It then converts the binary data back to text, extracting the original message and verifying the password.
    If the password matches, the hidden message is returned; otherwise, an error message is provided."""
    bdata = []
    full_text = []
    data_index = 0
    img = Image.open(img_path).convert('RGB')
    x, y = img.size
    pixel = img.load()
    rolling_data = ''
    for i in range(x):
        for j in range(y):
            r, g, b = pixel[i,j]
            bdata.append(str(r & 1))  #extract LSB of red pixel
            bdata.append(str(g & 1))  #extract LSB of green pixel
            bdata.append(str(b & 1))  #extract LSB of blue pixel
            while len(bdata) >= 8:
                byte = ''.join(bdata[:8])
                bdata = bdata[8:]
                char = chr(int(byte, 2))
                full_text.append(char)
                data_index = len(full_text)
                rolling_data += char
                if data_index == 5:  # Check for the prefix in the first 14 characters
                    if rolling_data != 'text:':
                        return "No hidden message found."
                if len(rolling_data) > 14:  # Keep only the last 14 characters for end detection
                    rolling_data = rolling_data[-14:]
                if rolling_data=='###====END====':
                    break
            if rolling_data=='###====END====':
                break
        if rolling_data=='###====END====':
            break
    main_text = re.split(r'###.*?###====END====', ''.join(full_text))[0]  # Extract text before password
    main_text = main_text.replace('text:', '', 1)  # Remove prefix
    decoded_password = re.search(r'###(.*?)###====END====', ''.join(full_text)).group(1)  # Extract password
    if decoded_password == password:
        return main_text
    else:
        return "Incorrect password"