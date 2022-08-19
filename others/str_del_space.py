def get_name():
    list1 = []
    with open('./demo.txt', 'r', encoding='utf-8') as file:
        list1.append(file.readlines())

    set1 = set(list1[0])
    print(set(list1[0]))
    print(len(set(list1[0])))
    list2 = list(set1)
    print(list2)
    for i in list2:
        print(i)


def del_space(in_name, out_name):
    end_data = []
    with open(in_name, 'r', encoding='utf-8') as file:
        list_data = file.readlines()
    print("list_data:", list_data)
    for value in list_data:
        end_data.append(str(value).strip('\n').strip())
    print('end_data:', end_data)
    with open(out_name, 'w', encoding='utf-8') as f:
        for i in end_data:
            f.write(i.strip() + '\n')


if __name__ == '__main__':
    del_space('./demo.txt', './demo_end.txt')
