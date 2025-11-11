import subprocess
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import os


def criar_driver_remote(profile_path):
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    # Se o Chrome padrão existir, tenta usar o modo de depuração remota
    if os.path.exists(chrome_path):
        print("Chrome encontrado. Tentando conectar via depuração remota...")

        # Ver se o Chrome com debug remoto já está rodando
        try:
            res = requests.get("http://localhost:9222/json", timeout=1)
            debug_ativo = res.status_code == 200
        except requests.exceptions.RequestException:
            debug_ativo = False

        if not debug_ativo:
            print("Chrome com depuração não está rodando. Iniciando...")

            subprocess.Popen(
                [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    "--remote-debugging-port=9222",
                    f"--user-data-dir={profile_path}",
                ]
            )
        else:
            print("Chrome debug está rodando")

        # Conecta o Selenium ao navegador já aberto
        options = Options()
        options.debugger_address = "127.0.0.1:9222"
        options.add_argument(
            "--ignore-certificate-errors"
        )  # Ignora aviso "Sua conexão não é particular"
        options.add_argument("--ignore-ssl-errors")
        # prefs = {"ssl_error_override_allowed": True}
        # options.add_experimental_option("prefs", prefs)
        # options.add_argument("--ignore-certificate-errors-spki-list")

        driver = webdriver.Chrome(options=options)

    else:
        print(
            "Chrome não encontrado no caminho padrão. Iniciando ChromeDriver normal..."
        )
        options = Options()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")

        # Usa o WebDriver Manager para baixar e configurar automaticamente o ChromeDriver
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

    return driver


def safe_action(driver, func, *args, **kwargs):
    # try:
    #     return func(*args, **kwargs)
    # except WebDriverException as e:
    #     print(f"[ERRO FATAL] Selenium quebrou: {e}. Reiniciando driver...")
    #     try:
    #         driver.quit()
    #     except Exception as e:
    #         pass
    #     driver = criar_driver_remote(r"C:/chrome_debug_profile")  # ou headless
    #     return driver  # devolve novo driver
    try:
        driver.quit()
    except Exception:
        pass
    driver = criar_driver_remote(r"C:/chrome_debug_profile")  # ou headless
    return driver  # devolve novo driver


def safe_click_js(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        driver.execute_script("arguments[0].click();", element)
    except Exception:
        element.click()
