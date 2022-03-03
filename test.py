from reprint import output
from time import sleep

def main():
    with output(output_type="list", initial_len=1, interval=0) as output_list:
        for i in [0,1,2,3]:
            output_list[0] = i
            sleep(1)
        
if __name__ == "__main__":
    main()