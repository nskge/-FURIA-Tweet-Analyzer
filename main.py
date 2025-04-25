import tweepy
import os
import time
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Carrega as variáveis do .env
load_dotenv()
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
client = tweepy.Client(bearer_token)

def coletar_tweets(query, qtd, lang):
    dados_tweets = []

    while True:
        try:
            tweets = client.search_recent_tweets(
                query=f"{query} lang:{lang} -is:retweet",
                max_results=min(qtd, 100),
                tweet_fields=["author_id", "created_at", "lang"]
            )

            if not tweets.data:
                print("Nenhum tweet encontrado.")
                break

            for tweet in tweets.data:
                dados_tweets.append({
                    "usuario": tweet.author_id,
                    "data": tweet.created_at,
                    "texto": tweet.text,
                    "sentimento": "",
                    "classificacao": ""
                })

            break  # Sucesso

        except tweepy.errors.TooManyRequests:
            print("Limite de requisições atingido. Aguardando 15 minutos...")
            time.sleep(15 * 60)

    return dados_tweets

def analisar_sentimento(dados_tweets):
    analyzer = SentimentIntensityAnalyzer()

    for tweet in dados_tweets:
        texto = tweet['texto']
        sentimento = analyzer.polarity_scores(texto)
        compound = sentimento['compound']
        tweet['sentimento'] = compound

   
        if compound >= 0.6:
            tweet['classificacao'] = 'Extremamente Positivo'
        elif compound >= 0.2:
            tweet['classificacao'] = 'Positivo'
        elif compound > -0.2:
            tweet['classificacao'] = 'Neutro'
        elif compound > -0.6:
            tweet['classificacao'] = 'Negativo'
        else:
            tweet['classificacao'] = 'Extremamente Negativo'

    return dados_tweets

def exibir_menu():
    print("\n==== Menu de Análise de Sentimentos ====")
    print("1. Coletar e Analisar Tweets")
    print("2. Sair")
    return input("Escolha uma opção: ")

def main():
    while True:
        opcao = exibir_menu()

        if opcao == "1":
            hashtag = input("Digite a hashtag ou termo (ex: #FURIA): ")
            qtd = int(input("Quantos tweets você quer buscar? (máx 100): "))
            lang = input("Idioma dos tweets (ex: pt, en, es): ")

            print(f"\nColetando até {qtd} tweets em '{lang}' com o termo '{hashtag}'...")
            tweets = coletar_tweets(hashtag, qtd, lang)

            print("Analisando sentimentos...")
            tweets_analisados = analisar_sentimento(tweets)

            print("\n==== Resultados ====")
            for tweet in tweets_analisados:
                print(f"\nUsuário: {tweet['usuario']}")
                print(f"Data: {tweet['data']}")
                print(f"Sentimento: {tweet['classificacao']} ({tweet['sentimento']})")
                print(f"Texto: {tweet['texto']}")
                print("===================================")

        elif opcao == "2":
            print("Valeu! Até a próxima.")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
