# 消防规范网：https://gf.cabr-fire.com/m/

if __name__ == "__main__":
    # 调用其他.py文件的方法，获取信息
    from data_script3 import process_level1
    from data_script3 import save_to_csv
    process_level1()
    save_to_csv('消防规范网.csv')
    # 执行完成后会自动生成 消防规范网.csv 文件