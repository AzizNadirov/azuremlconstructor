# Loads data inputs to the program
import argparse
import pandas as pd


parser = argparse.ArgumentParser()

 
parser.add_argument('--dwh_files', type=str) 
parser.add_argument('--dwh_files', type=str) 
parser.add_argument('--dwh_files', type=str) 
parser.add_argument('--dwh_files', type=str) 
parser.add_argument('--ds_root', type=str) 
parser.add_argument('--category_tree', type=str)

args = parser.parse_args()


products = pd.read_parquet(args.dwh_files + "/mp_products_mpn_gtin.parquet")

specs = pd.read_parquet(args.dwh_files + "/mp_price_comparision_all_products_chars.parquet")

ff_cats = pd.read_csv(args.dwh_files + "/ff_product_categories.csv")

ff_products = pd.read_parquet(args.dwh_files + "/umico_ff_products.parquet")

ds_root = args.ds_root

mp_all_category_tree_prod = pd.read_parquet(args.category_tree + "/mp_all_category_tree_prod.parquet")
