from amlctor.input import FileInputSchema, PathInputSchema
from amlctor.core import StepSchema

# --------------------------| Module Names |----------------------------
AML_MODULE_NAME: str =       'aml'
SCRIPT_MODULE_NAME: str =    'script'
DATALOADER_MODULE_NAME: str = 'data_loader'



# ---------------------------| General |---------------------------------

NAME = "mp-ds-find-inner-duplicates"
DESCRIPTION = "Does mp inner duplicate detection using different approaches "


# ---------------------------| DataInputs |-------------------------------


ds = "mp_ds_find_duplicates"
ds_populars = "mpdspopularproducts"

dwh_files = FileInputSchema(
                        name='dwh_files', 
                        datastore_name=ds, 
                        path_on_datastore='dwh/', 
                        files = ['mp_products_mpn_gtin.parquet', 
                                 "mp_price_comparision_all_products_chars.parquet",
                                 "ff_product_categories.csv",
                                 'umico_ff_products.parquet'], 
                        data_reference_name = ''
    )

category_tree = FileInputSchema(
                        name='category_tree', 
                        datastore_name=ds_populars, 
                        path_on_datastore='data/dwh/', 
                        files = ["mp_all_category_tree_prod.parquet"], 
                        data_reference_name = ''
    )

ds_root = PathInputSchema(
                        name='ds_root', 
                        datastore_name=ds, 
                        path_on_datastore='',
                        data_reference_name=''
    )

# ---------------------------| Steps |---------------------------------

find_dups = StepSchema(
                        name='find_dups',
                        compute_target='goodboy', 
                        input_data=[dwh_files, ds_root, category_tree], 
                        allow_reuse=True
            )



step2 = StepSchema(
                        name='step2',
                        compute_target='goodboy', 
                        input_data=[dwh_files, ds_root, category_tree], 
                        allow_reuse=True
            )




STEPS = [find_dups, ]



# ---------------------------| extra |---------------------------------


EXTRA = {
            'continue_on_step_failure': False,
}
