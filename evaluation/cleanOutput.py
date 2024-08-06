import os
from pathlib import Path

pathList = Path("./postgres/queries-outp/").glob('**/*.json')

for path in pathList:

    #if str(path) == "postgres/queries-outp/test.json":
        print (path)
        json = ""
        with open(path, "r+") as f:
            
            old = ""
            firstBracket = False
            for line in f.read():
                
                # remove everything before real json
                if not firstBracket:
                    if line[0] == "[":
                        firstBracket = True
                        old += line
                    continue
                
                old += line
                

            json = old.replace(" ", "")
            json = json.replace("+", "")
            json = json.replace("(1row)", "")
            #if old.
            # print(json)
            f.seek(0) # rewind
            f.truncate()
            f.write(json) # write the new line before
            f.close()
