from app import app

if __name__ == '__main__':
    with app.test_client() as c:
        resp = c.get('/analysis')
        print('STATUS:', resp.status_code)
        print(resp.data.decode('utf-8'))
