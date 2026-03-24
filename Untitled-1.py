import sqlite3

def run_tests():
    # 1. 创建内存数据库
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # 2. 建表 (Schema)
    cursor.executescript('''
    CREATE TABLE BOOK (Book_ID TEXT PRIMARY KEY, Title TEXT, Publisher_ID TEXT, Category TEXT);
    CREATE TABLE AUTHORS (Book_ID TEXT, Author_name TEXT, Gender TEXT, Nationality TEXT);
    CREATE TABLE PUBLISHER (Publisher_ID TEXT PRIMARY KEY, Publisher_name TEXT, Country TEXT, City TEXT);
    CREATE TABLE BOOK_LOANS (Book_ID TEXT, Branch_ID TEXT, Card_NO TEXT, Date_out TEXT, Due_date TEXT, Status TEXT);
    CREATE TABLE LIBRARY_BRANCH (Branch_ID TEXT PRIMARY KEY, Branch_name TEXT, City TEXT);
    CREATE TABLE BOOK_STORAGE (Book_ID TEXT, Branch_ID TEXT, Quantity INTEGER);
    CREATE TABLE BORROWERS (Card_NO TEXT PRIMARY KEY, Phone TEXT, Name TEXT, Gender TEXT, City TEXT);
    ''')

    # 3. 插入测试数据 (Edge Cases)
    cursor.executescript('''
    -- 借阅者: Alice(全能借阅者), Bob(普通借阅者), Charlie(从未借书)
    INSERT INTO BORROWERS VALUES ('C01', '123', 'Alice', 'F', 'CityA');
    INSERT INTO BORROWERS VALUES ('C02', '456', 'Bob', 'M', 'CityB');
    INSERT INTO BORROWERS VALUES ('C03', '789', 'Charlie', 'M', 'CityC'); 

    -- 分馆: Central 和 North
    INSERT INTO LIBRARY_BRANCH VALUES ('BR1', 'Central', 'CityA');
    INSERT INTO LIBRARY_BRANCH VALUES ('BR2', 'North', 'CityB');

    -- 出版社: UK 和 US
    INSERT INTO PUBLISHER VALUES ('P01', 'Oxford Press', 'UK', 'London');
    INSERT INTO PUBLISHER VALUES ('P02', 'MIT Press', 'USA', 'NY');

    -- 书籍: 包含 Data Science 和 Fiction
    INSERT INTO BOOK VALUES ('B01', 'Intro to DS', 'P01', 'Data Science');
    INSERT INTO BOOK VALUES ('B02', 'Advanced ML', 'P01', 'Data Science');
    INSERT INTO BOOK VALUES ('B03', 'Harry Potter', 'P01', 'Fiction');
    INSERT INTO BOOK VALUES ('B04', 'Dune', 'P02', 'Fiction');

    -- 作者: Alan(写了DS和Fiction, 即所有分类), Turing(只写了DS)
    INSERT INTO AUTHORS VALUES ('B01', 'Alan', 'M', 'UK');
    INSERT INTO AUTHORS VALUES ('B03', 'Alan', 'M', 'UK');
    INSERT INTO AUTHORS VALUES ('B02', 'Turing', 'M', 'UK');

    -- 借阅记录:
    -- Alice 借了 B01 和 B02 (所有 Data Science)
    INSERT INTO BOOK_LOANS VALUES ('B01', 'BR1', 'C01', '2023-01-01', '2023-02-01', 'Returned');
    INSERT INTO BOOK_LOANS VALUES ('B02', 'BR2', 'C01', '2023-01-02', '2023-02-02', 'Returned');
    -- Bob 在 Central 借了 B03
    INSERT INTO BOOK_LOANS VALUES ('B03', 'BR1', 'C02', '2023-01-03', '2023-02-03', 'Returned');

    -- 库存记录: Central 总量最高
    INSERT INTO BOOK_STORAGE VALUES ('B01', 'BR1', 50); -- Central: 50本 P01(UK)
    INSERT INTO BOOK_STORAGE VALUES ('B03', 'BR1', 60); -- Central: 60本 P01(UK)
    INSERT INTO BOOK_STORAGE VALUES ('B02', 'BR2', 30); -- North: 30本 P01(UK)
    ''')

    def print_result(q_title, expected, sql):
        print(f"\n{q_title}")
        print(f"预期结果: {expected}")
        print("实际结果: ", end="")
        try:
            results = cursor.execute(sql).fetchall()
            print([row[0] if len(row) == 1 else row for row in results])
        except Exception as e:
            print(f"执行错误: {e}")

    # ==========================
    # 验证环节 (SQL 等价替换你的关系代数)
    # ==========================

    # Q1. 从未借书的人 (差集模拟: 所有借阅者 EXCEPT 借过书的借阅者)
    print_result("--- Q1 ---", "['Charlie']", '''
        SELECT Name FROM BORROWERS
        EXCEPT
        SELECT B.Name FROM BORROWERS B JOIN BOOK_LOANS L ON B.Card_NO = L.Card_NO;
    ''')

    # Q2. 在 "Central" 借过书的人 (自然连接模拟)
    print_result("--- Q2 ---", "['Alice', 'Bob']", '''
        SELECT DISTINCT B.Name 
        FROM BORROWERS B 
        JOIN BOOK_LOANS L ON B.Card_NO = L.Card_NO
        JOIN LIBRARY_BRANCH LB ON L.Branch_ID = LB.Branch_ID
        WHERE LB.Branch_name = 'Central';
    ''')

    # Q3. 总库存最高的分馆 (利用 WITH 子句模拟你的 Let 赋值)
    print_result("--- Q3 ---", "['Central']", '''
        WITH Inv AS (
            SELECT Branch_ID, SUM(Quantity) AS Total_Inv FROM BOOK_STORAGE GROUP BY Branch_ID
        ),
        BranchInv AS (
            SELECT LB.Branch_name, I.Total_Inv 
            FROM LIBRARY_BRANCH LB JOIN Inv I ON LB.Branch_ID = I.Branch_ID
        )
        SELECT Branch_name FROM BranchInv 
        WHERE Total_Inv = (SELECT MAX(Total_Inv) FROM BranchInv);
    ''')

    # Q4. 在每个分类都写过书的作者 (双重 NOT EXISTS 模拟除法)
    print_result("--- Q4 ---", "['Alan']", '''
        SELECT DISTINCT A1.Author_name 
        FROM AUTHORS A1
        WHERE NOT EXISTS (
            SELECT DISTINCT Category FROM BOOK
            EXCEPT
            SELECT B.Category FROM AUTHORS A2 JOIN BOOK B ON A2.Book_ID = B.Book_ID
            WHERE A2.Author_name = A1.Author_name
        );
    ''')

    # Q5. 借阅了所有 'Data Science' 书籍的人 (EXCEPT 模拟除法)
    print_result("--- Q5 ---", "['Alice']", '''
        SELECT Name FROM BORROWERS B
        WHERE NOT EXISTS (
            SELECT Book_ID FROM BOOK WHERE Category = 'Data Science'
            EXCEPT
            SELECT Book_ID FROM BOOK_LOANS L WHERE L.Card_NO = B.Card_NO
        );
    ''')

    # Q6. 各分馆名称及其英国出版商的书籍总数
    print_result("--- Q6 ---", "[('Central', 110), ('North', 30)]", '''
        SELECT LB.Branch_name, SUM(S.Quantity) AS Total
        FROM LIBRARY_BRANCH LB
        JOIN BOOK_STORAGE S ON LB.Branch_ID = S.Branch_ID
        JOIN BOOK B ON S.Book_ID = B.Book_ID
        JOIN PUBLISHER P ON B.Publisher_ID = P.Publisher_ID
        WHERE P.Country = 'UK'
        GROUP BY LB.Branch_ID, LB.Branch_name;
    ''')

    conn.close()

if __name__ == '__main__':
    run_tests()