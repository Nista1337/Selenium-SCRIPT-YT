from utils.Application import Application


if __name__ == "__main__":
    request = input('Введите запрос: ')
    app = Application(request=request)
    app.run()
