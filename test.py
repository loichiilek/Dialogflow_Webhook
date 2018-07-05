import json


def run_nlu():
    a_dict = eval(open('keyword.txt', 'r').read())

    while True:
        try:
            for key, value in a_dict.items():
                print(str(key) + ": " + str(value))

            key = input("Enter keyword: ")
            value = input("Enter definition: ")

            a_dict[key] = value

            with open('keyword.txt', 'w') as file:
                file.write(json.dumps(a_dict))


        # Press ctrl-c or ctrl-d on the keyboard to exit
        except (KeyboardInterrupt, EOFError, SystemExit):
            break


if __name__ == '__main__':
    run_nlu()


