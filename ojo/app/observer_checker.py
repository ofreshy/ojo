from ojo.config import config


from ojo import builder

if __name__ == "__main__":
    print("START WATCHER CHECKER")
    this_config = config.load()

    app_builder = builder.Builder(this_config)

    app = app_builder.build()
    app.start()

