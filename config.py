# config.py
BASE_URL = "https://raw.githubusercontent.com/JuliaDetoni/4SEM_PI_MINERACAO_DADOS/main/dataset"

DATASETS = {
    'customers':    f"{BASE_URL}datasetolist_customers_dataset.csv",
    'geolocation':  f"{BASE_URL}dataset/olist_geolocation_dataset.csv",
    'order_items':  f"{BASE_URL}dataset/olist_order_items_dataset.csv",
    'payments':     f"{BASE_URL}dataset/olist_order_payments_dataset.csv",
    'reviews':      f"{BASE_URL}dataset/olist_order_reviews_dataset.csv",
    'orders':       f"{BASE_URL}dataset/olist_orders_dataset.csv",
    'products':     f"{BASE_URL}dataset/olist_products_dataset.csv",
    'sellers':      f"{BASE_URL}dataset/olist_sellers_dataset.csv",
}
