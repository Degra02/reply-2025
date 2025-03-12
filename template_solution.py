from parser import parser
import sys



file =  int(sys.argv[1]) if len(sys.argv) > 1 else 0
budget, resources, turn = parser(file)

  