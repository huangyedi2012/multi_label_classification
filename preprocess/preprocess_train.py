import argparse
import os.path
import pandas as pd

from timer import Timer


def read_df(filepath):
    print(f"read data from {filepath}")
    if 'csv' in filepath:
        df = pd.read_csv(filepath, sep='\t', encoding='utf8')
    elif 'xlsx' in filepath:
        df = pd.read_excel(filepath)
    else:
        raise TypeError(f'input file [{filepath}] type not support! ')
    df = df.iloc[:, [0, 1]]
    df.columns = ['意图', '话术']
    return df


def split(df, ratio=0.9, seed=831):
    print(f"split train test with frac={ratio}")
    train_df_list = []
    test_df_list = []
    intent_group = df.groupby('意图')
    for intent, group in intent_group:
        train_group = group.sample(frac=ratio, random_state=seed)
        test_group = group.drop(train_group.index)
        train_df_list.append(train_group)
        test_df_list.append(test_group)
    return pd.concat(train_df_list).reset_index(drop=True), pd.concat(test_df_list).reset_index(drop=True)


def print_df_statics(df, desc=''):
    n_class = df['意图'].nunique()
    n_text = df['话术'].nunique()
    print(f"df length [{len(df)}], with [{n_text}] text and [{n_class}] class. {desc}")


if __name__ == '__main__':
    timer = Timer()
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', required=True)
    parser.add_argument('--not_split', action='store_true')
    parser.add_argument('--ratio', type=float, default=0.9)
    parser.add_argument('--filter_less', action='store_true')
    parser.add_argument('--filter_size', type=int, default=30)
    parser.add_argument('--sample_size', type=int, default=-1)
    parser.add_argument('--seed', type=int, default=831)
    args = parser.parse_args()
    print(args)

    base_dir = os.path.dirname(args.input_file)
    class_file = os.path.join(base_dir, 'class.txt')

    df = read_df(filepath=args.input_file)

    # explode intention list
    df['意图'] = df['意图'].apply(lambda x: x.strip().split(','))
    df = df.explode('意图').reset_index(drop=True)
    print_df_statics(df, 'raw data')

    # 是否过滤量级较少的数据
    if args.filter_less:
        print(f"filter data less than {args.filter_size}")
        df = pd.concat([x for _, x in df.groupby('意图') if len(x) >= args.filter_size]).reset_index(drop=True)
        print_df_statics(df, 'after filter less label')

    # 生成class文件
    label_list = sorted(df['意图'].unique())
    print(f"write class file to {class_file}")
    with open(class_file, 'w', encoding='utf8') as fw:
        for label in label_list:
            fw.write(f"{label}\n")

    # 将多意图话术合并
    df = df.groupby('话术')['意图'].apply(lambda x: ','.join(sorted(set(x)))).to_frame().reset_index()
    print_df_statics(df, "after merge multi intent")

    # 是否需要切分数据集
    train_df = None
    test_df = None
    if not args.not_split:
        train_df, test_df = split(df, args.ratio, args.seed)
        print_df_statics(train_df, "train df")
        print_df_statics(test_df, "test df")

    # 是否过采样
    if args.sample_size > 0:
        print(f"sample data with sample size: {args.sample_size}")
        df = df.groupby('意图').apply(lambda x: x.sample(n=args.sample_size) if len(x) >= args.sample_size else x.sample(n=args.sample_size, replace=True)).reset_index(drop=True)
        train_df = train_df.groupby('意图').apply(lambda x: x.sample(n=args.sample_size) if len(x) >= args.sample_size else x.sample(n=args.sample_size, replace=True)).reset_index(drop=True)

        print_df_statics(df, "df after sample")
        print_df_statics(train_df, "train df after sample")
    # 保存划分结果
    print(f"write all.csv")
    df.to_csv(os.path.join(base_dir, 'all.csv'), sep='\t', index=False)
    if train_df is not None:
        print(f"write train.csv")
        train_df.to_csv(os.path.join(base_dir, 'train.csv'), sep='\t', index=False)
        print(f"write test csv")
    if test_df is not None:
        test_df.to_csv(os.path.join(base_dir, 'test.csv'), sep='\t', index=False)
