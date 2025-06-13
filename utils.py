# utils.py

import yfinance as yf
import pandas as pd
import ta
import time

def descargar_datos(ticker="BTC-USD", periodo="1d", intervalo="1m"):
    """
    Descarga datos históricos desde Yahoo Finance con reintentos
    
    Args:
        ticker (str): Ticker del activo (ej: BTC-USD)
        periodo (str): Período de datos (ej: '1d')
        intervalo (str): Intervalo entre datos (ej: '1m' = 1 minuto)

    Returns:
        pd.DataFrame, pd.Series: Datos procesados y serie Close
    """
    for i in range(3):
        print(f"🔄 Descargando datos de {ticker}... (intento {i+1})")
        try:
            data = yf.download(ticker, period=periodo, interval=intervalo, auto_adjust=True, progress=False)

            if isinstance(data.columns, pd.MultiIndex):
                print("🔹 Ajustando columnas multinivel...")
                data.columns = [col[0] for col in data.columns]
            
            data.columns = [col.lower() for col in data.columns]

            if len(data) == 0:
                raise ValueError("Datos vacíos devueltos por Yahoo Finance")

            close_series = data['close'].squeeze()
            return data, close_series

        except Exception as e:
            print(f"⚠️ Error en intento {i+1}: {e}")
            if i < 2:
                print("⏳ Reintentando en 5 segundos...")
                time.sleep(5)

    print("❌ No se pudo descargar datos después de varios intentos")
    return pd.DataFrame(), pd.Series()


def calcular_indicadores(data, close_series):
    """
    Calcula RSI, MACD, SMA_20 y SMA_50 si hay suficientes datos
    
    Args:
        data (pd.DataFrame): Datos del activo
        close_series (pd.Series): Serie temporal del precio Close

    Returns:
        pd.DataFrame: Datos con indicadores técnicos
    """
    if data.empty or len(data) < 20:
        print("❌ No hay suficientes datos para calcular indicadores")
        return data

    print("📊 Calculando indicadores técnicos...")
    data['RSI'] = ta.momentum.RSIIndicator(close_series, window=14).rsi()
    data['MACD'] = ta.trend.MACD(close_series).macd()
    data['SMA_20'] = close_series.rolling(window=20).mean()
    data['SMA_50'] = close_series.rolling(window=50).mean()

    data = data.dropna()
    return data