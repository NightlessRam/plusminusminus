
def decode_percent(percentEncoded: str):
    if '%' in percentEncoded:
        temp = ""
        i=0
        while i < len(percentEncoded):
            if(percentEncoded[i] == '%'):
                dumpPercent = percentEncoded[i:i+3]
                if dumpPercent == '%21':
                    temp += '!'
                    i+=3
                elif dumpPercent == '%40':
                    temp += '@'
                    i+=3
                elif dumpPercent == '%23':
                    temp += '#'
                    i+=3
                elif dumpPercent == '%24':
                    temp += '$'
                    i+=3
                elif dumpPercent == '%25':
                    temp += '%'
                    i+=3
                elif dumpPercent == '%5E':
                    temp += '^'
                    i+=3
                elif dumpPercent == '%26':
                    temp += '&'
                    i+=3
                elif dumpPercent == '%28':
                    temp += '('
                    i+=3
                elif dumpPercent == '%29':
                    temp += ')'
                    i+=3
                elif dumpPercent == '%2D':
                    temp += '-'
                    i+=3
                elif dumpPercent == '%5F':
                    temp += '_'
                    i+=3
                elif dumpPercent == '%3D':
                    temp += '=' 
                    i+=3
            else:
                temp += percentEncoded[i]
                i+=1
        return temp
    return percentEncoded

def validate_password(password: str):
    if len(password)<8: #at least 8
        return False

    lowerExist = False
    upperExist = False
    num = False
    specialChar = False
    invalid = True
    for characters in password: 
        characters = str(characters)
        if characters.islower():
            lowerExist = characters.islower()
        if characters.isupper():
            upperExist = characters.isupper()
        if characters.isnumeric():
            num = characters.isnumeric()
        if characters in  {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}:
            specialChar = True
        if not ((characters.isalnum()) or (characters in {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='})):
            invalid = False
    if not lowerExist:
        return False
    if not upperExist:
        return False
    if not num:
        return False
    if not specialChar:
        return False
    if invalid == False:
        return False
    
    return True