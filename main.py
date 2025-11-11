import os
import signal
import atexit
import datetime
import time
import math

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from modules.selenium_config import *
from modules.gui import *

TOTAL_PROMPTS_DESEJADOS = 3

def escrever_mensagem_chatgpt(driver, mensagem):
    wait = WebDriverWait(driver, 20)

    campo = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ProseMirror#prompt-textarea"))
    )

    # clica para focar e envia o texto
    campo.click()
    campo.clear()
    for parte in mensagem.split('\n'):
        campo.send_keys(parte)
        campo.send_keys(Keys.SHIFT, Keys.ENTER)
        time.sleep(0.1)

    # aguarda o botão de enviar ficar clicável
    botao_enviar = wait.until(
        EC.element_to_be_clickable((By.ID, "composer-submit-button"))
    )

    # clica no botão de enviar
    botao_enviar.click()


def ler_resposta_chatgpt(driver):
    wait = WebDriverWait(driver, 30)

    # --- ESPERA UMA NOVA RESPOSTA ---
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-message-author-role='assistant']")))
    respostas = driver.find_elements(By.CSS_SELECTOR, "div[data-message-author-role='assistant']")
    ultima_resposta = respostas[-1]

    # --- ESPERA O TEXTO PARAR DE MUDAR (stream concluído) ---
    texto_anterior = ""
    estavel = 0

    # Verifica até 30s se o texto se estabiliza
    for _ in range(30):
        texto_atual = ultima_resposta.text.strip()
        if texto_atual == texto_anterior and len(texto_atual) > 0:
            estavel += 1
            if estavel >= 3:  # 3 ciclos seguidos sem mudança = terminou
                break
        else:
            estavel = 0
        texto_anterior = texto_atual
        time.sleep(1)

    retorno_chatbot = texto_atual

    return retorno_chatbot


def gerar_texto_para_chatgpt_var(nome, texto, variacao, quantidade):
    mensagem = f"""
        Gere {quantidade} prompts criativos para o KREA baseados na seguinte descrição:

        "{texto}", 
        
        com a variação: "{variacao}"

        Cada prompt deve ser independente e único, pronto para uso direto no KREA.

        Regras:
        - Escreva apenas os prompts, um por linha.
        - Sem numeração, sem aspas, sem explicações.
        - Prompts realistas, variados e criativos.

        Retorne apenas os prompts, um por linha, sem nenhum outro texto.
        """
    

    return mensagem


def enviar_prompts_krea(driver, prompts_por_variacao):

    wait = WebDriverWait(driver, 30)

    for variacao, lista_prompts in prompts_por_variacao.items():
        while True:
            try:
                print(f"Variação {variacao}:")
                for prompt in lista_prompts:
                    # Aguarda o <textarea> estar presente e visível
                    try:
                        textarea = WebDriverWait(driver, 5).until(
                            EC.visibility_of_element_located((By.ID, "prompt"))
                        )
                    except:
                        textarea = wait.until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea[name='Prompt']"))
                        )

                    # Limpa e insere o texto
                    textarea.click()
                    textarea.clear()
                    textarea.send_keys(prompt)

                    # Aguarda o botão "Generate" estar clicável
                    try:
                        generate_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((
                                By.XPATH,
                                "//button[.//span[normalize-space(text())='Generate']]"
                            ))
                        )
                    except:
                        generate_button = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Generate']"))
                        )

                    # Clica no botão
                    generate_button.click()
                    
                    time.sleep(5)  # espera entre cada envio
                break
            except:
                time.sleep(1)
                continue


def main():
    print("[INÍCIO] Iniciando o script de automação no PJe...")
    os.makedirs(r"C:/chrome_debug_profile", exist_ok=True)

    print("[NAVEGADOR] Criando instância do navegador com perfil remoto...")
    driver = criar_driver_remote(r"C:/chrome_debug_profile")

    
    resultado = mostrar_janela_dados()
    if resultado is None:
        return
    nome = resultado["nome"]
    texto = resultado["texto"]
    variacoes = resultado["variacoes"]
    # nome = "Roberto"
    # texto = "55 anos, pele clara, cabelo grisalho, óculos, sorrindo, vestindo camisa social azul, fundo de escritório moderno"
    # variacoes = ["estilo futurista", "arte digital vibrante", "realismo fotográfico"]

    try:
        print("[LOGIN] Realizando login no sistema...")
        # input("Entre no chatgpt, faça o login e aperte Enter.")
        mostrar_janela_mensagem("Por favor, faça login no ChatGPT na janela do navegador aberta. Depois de logar, clique em OK para continuar.")
    except Exception as e:
        print(f"[ERRO] Erro encontrado durante a execução: {e}")
        mostrar_notificacao("[ERRO] Erro no script. Não foi possível executar.")
        return


    mensagens_para_chatgpt = []
    prompts_por_variacao = {}



    # === GERAÇÃO AUTOMÁTICA DAS MENSAGENS COM DISTRIBUIÇÃO ===

    qtd_variacoes = len(variacoes)

    # Calcula base proporcional (inteira)
    base_qtd = TOTAL_PROMPTS_DESEJADOS // qtd_variacoes
    resto = TOTAL_PROMPTS_DESEJADOS % qtd_variacoes  # se não dividir exato, distribui o resto

    # Exemplo: 50 / 3 = 16 cada, resto = 2 → duas variações recebem +1
    quantidades_por_variacao = [
        base_qtd + (1 if i < resto else 0) for i in range(qtd_variacoes)
    ]

    print("Distribuição planejada:")
    for i, qtd in enumerate(quantidades_por_variacao, start=1):
        print(f"  - Variação {i}: {qtd} prompts")

    # Gera mensagens para cada variação conforme sua quantidade
    for i, variacao in enumerate(variacoes):
        quantidade = quantidades_por_variacao[i]
        mensagens_para_chatgpt.append(gerar_texto_para_chatgpt_var(nome, texto, variacao, quantidade=quantidade))



    for idx, mensagem in enumerate(mensagens_para_chatgpt, start=1):
        # While true para manter o script rodando, e reiniciando o driver se ele cair.
        while True:
            try:
                print(f"\n=== Enviando variação {idx}: {variacoes[idx-1]} ===")
                escrever_mensagem_chatgpt(driver, mensagem)

                while True:
                    try:
                        resposta = ler_resposta_chatgpt(driver)
                        break
                    except:
                        time.sleep(1)
                        continue

                # Divide em prompts (um por linha)
                prompts = [linha.strip() for linha in resposta.split('\n') if linha.strip()]
                # Salva na lista correspondente
                prompts_por_variacao[idx] = prompts

                print(f"[OK] {len(prompts)} prompts capturados para variação {idx}.")

                break

            except KeyboardInterrupt:
                print(
                    "[INTERRUPÇÃO] Execução interrompida pelo usuário (Ctrl+C). Salvando relatório parcial..."
                )
                break

            except Exception as e:
                print(f"[ERRO] Erro encontrado durante a execução: {e}")
                driver = safe_action(driver, lambda: None)  # reinicia navegador
                continue


    print("\n=== Enviando prompts gerados para o KREA ===")
    driver.get("https://www.krea.ai/image")
    time.sleep(1)
    enviar_prompts_krea(driver, prompts_por_variacao)
    

    print("[OK] Script finalizado. Pode fechar o navegador.")
    mostrar_notificacao("[OK] Script finalizado. Pode fechar o navegador.")


if __name__ == "__main__":
    main()
    





