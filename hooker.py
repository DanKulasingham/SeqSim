import sys
from os import path

sys.path.append(path.join(path.dirname(sys.argv[0]), "lib"))    # for pyd
sys.path.append(path.join(path.dirname(sys.argv[0]), "windll"))  # for dll
