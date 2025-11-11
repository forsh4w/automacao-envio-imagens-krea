import os
import json
import base64
import requests
from dotenv import load_dotenv

# === CONFIGURAÇÕES ===
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL = "openai/gpt-5-nano"  # ou outro multimodal do OpenRouter
OUTPUT_JSON = "selected_images.json"

def encode_image(image_path):
    """Lê e converte a imagem para base64 data URL"""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = image_path.split(".")[-1].lower()
    mime = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
    return f"data:{mime};base64,{b64}"

def avaliar_grupo(prompt_id, imagens):
    """Envia um grupo de 5 imagens e retorna as 2 melhores"""
    print(f"🔎 Avaliando prompt {prompt_id} ({len(imagens)} imagens)...")

    # Monta o conteúdo da mensagem
    conteudo = [
        {"type": "text", "text": (
            f"As seguintes 5 imagens pertencem ao mesmo prompt (grupo {prompt_id}).\n"
            "Avalie qualidade, realismo e ausência de erros anatômicos.\n"
            "Escolha as 2 melhores e RETORNE SOMENTE UM JSON VÁLIDO no formato:\n"
            "{\n"
            '  "melhores": ["nome1.png", "nome2.png"]\n'
            "}\n"
            "Use exatamente os nomes fornecidos.\n"
            "Não escreva nada fora desse JSON. Não explique. Apenas retorne o JSON."
        )}
    ]

    for img in imagens:
        nome_arquivo = os.path.basename(img)
        conteudo.append({"type": "text", "text": f"Imagem: {nome_arquivo}"})
        conteudo.append({
            "type": "image_url",
            "image_url": {"url": encode_image(img)}
        }) # type: ignore

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": conteudo}]
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "temperature": "0.3"  # força respostas mais determinísticas
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=180
    )

    if response.status_code != 200:
        print("❌ Erro:", response.status_code, response.text)
        return []

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    print(f"Content: {content}\n\n")
    try:
        parsed = json.loads(content)
        return parsed.get("melhores", [])
    except Exception:
        print("⚠️ Falha ao interpretar resposta:", content)
        return []

def melhores_fotos(input_dir):
    todas = sorted(os.listdir(input_dir))
    resultados = {"selected_images": []}

    # Divide as imagens em grupos de 5
    for i in range(0, len(todas), 5):
        grupo = todas[i:i+5]
        prompt_id = (i // 5) + 1
        caminhos = [os.path.join(input_dir, img) for img in grupo]

        melhores = avaliar_grupo(prompt_id, caminhos)
        for m in melhores:
            resultados["selected_images"].append(m)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    return resultados

