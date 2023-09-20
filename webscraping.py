import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

def buscar_elemento(driver, by, valor):
    '''
    Busca un elemento en la página 
    Si no lo encuentra, retorna N/A
    '''
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((by, valor)))
        elemento = driver.find_element(by, valor)
        return elemento.text.strip()
    except:
        return "N/A"
    
# Configurar las opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_experimental_option("detach", True)

# Crear una instancia del navegador Chrome
driver = webdriver.Chrome(options=chrome_options)

# Crear un DataFrame para almacenar los datos
profile = pd.DataFrame(columns=['Link', 'Título anuncio', 'Descripción', 'Código',
                                'Tipo de inmueble', 'Valor en $ (Pesos)', 'Valor en UF', 'Fecha de publicación',
                                'Dormitorios', 'Baños', 'Nombre contacto', 'Comuna', 'Superficie total',
                                'Contacto URL'])

# URL de la página principal 
myUrl ='https://www.yapo.cl/region-metropolitana/arrendar?ca=15_s&l=0&w=1&cmn=%20&%20cmn%20=%20301%20&%20ret%20=%201'
# Visitar la página principal
driver.get(myUrl)

# Esperar a que la página cargue completamente
wait = WebDriverWait(driver, 10)
wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "/html/body/app-root/listing-index/listing-main/div[2]/div/div/listing-result-list/app-paginator/a[2]")))

# Obtener el número de páginas
lastPageElement = driver.find_element(By.XPATH, "/html/body/app-root/listing-index/listing-main/div[2]/div/div/listing-result-list/app-paginator/a[2]")
lastPage = int(lastPageElement.get_attribute("href").split("=")[-1])

# Se recorren las páginas
for i in range(1):
    url = f'{myUrl}&page={i+1}'
    sleep(5)
    driver.get(url)

    # Esperar a que los anuncios carguen completamente
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[@class='card d-flex flex-row align-self-stretch flex-fill inmo subcategory-1240 category-1000 horizontal has-cover']")))
    
    # Se obtienen los links de los anuncios de la página actual
    links = driver.find_elements(By.XPATH, "//a[@class='card d-flex flex-row align-self-stretch flex-fill inmo subcategory-1240 category-1000 horizontal has-cover']")
    urls_links = []

    for link in links:
        link_url = link.get_attribute('href')
        urls_links.append(link_url)

    # Se revisa cada anuncio
    for link in urls_links:
        h1, h2, h3, h4, h5, h6, h7, h8, h9, h10, h11, h12 = 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A' 
        sleep(2)
        driver.get(link)
        # Título anuncio
        h1 = buscar_elemento(driver, By.XPATH, "/html/body/app-root/adview-index/div[1]/div/div[1]/div/adview-price-info/h1")
        # Fecha publicación
        h2 = buscar_elemento(driver, By.XPATH, "/html/body/app-root/adview-index/div[1]/div/div/div/adview-price-info/div/div[2]/p").replace('\n', ' ').replace('\t', '')
        # Nombre contacto
        h3 = buscar_elemento(driver, By.CLASS_NAME, "seller-name")
        # Precio
        h4 = buscar_elemento(driver, By.CLASS_NAME, "price").replace('\n', ' ').replace('\t', '')
        # Precio UF
        h5 = buscar_elemento(driver, By.CLASS_NAME, "currency-price").replace('\n', ' ').replace('\t', '')
        # Tipo inmueble                                       
        h6 = buscar_elemento(driver, By.XPATH, "/html/body/app-root/adview-index/div[1]/div/div/adview-features/div[2]/p[2]")
        # Comuna
        h7 = buscar_elemento(driver, By.XPATH, "/html/body/app-root/adview-index/div[1]/div/div/div/adview-price-info/div/div[1]/p")
        # Superficie total
        h8 = buscar_elemento(driver, By.XPATH, "/html/body/app-root/adview-index/div[1]/div/div/adview-features/div[4]/p[2]")  
        # N° Dormitorios
        h9 = buscar_elemento(driver, By.XPATH, "/html/body/app-root/adview-index/div[1]/div/div/adview-features/div[4]/p[2]")     
        # N° Baños
        h10 = buscar_elemento(driver, By.XPATH, "/html/body/app-root/adview-index/div[1]/div/div/adview-features/div[5]/p[2]")      
        # Código
        h11 = buscar_elemento(driver, By.XPATH, "/html/body/app-root/adview-index/div[1]/div/div/adview-features/div[1]/p[2]")     
        # Descripción
        h12 = buscar_elemento(driver, By.XPATH, "/html/body/app-root/adview-index/div[1]/div/div/adview-description/div/p").replace('\n', ' ')       
        # Url Contacto
        h13 = 'N/A'  # Este campo solo es accesible al iniciar sesión
        
        ser = pd.Series([link, h1, h12, h11, h6, h4, h5, h2, h9, h10, h3, h7, h8, h13],
                        index=['Link', 'Título anuncio', 'Descripción', 'Código','Tipo de inmueble', 
                               'Valor en $ (Pesos)', 'Valor en UF', 'Fecha de publicación','Dormitorios', 
                               'Baños', 'Nombre contacto', 'Comuna', 'Superficie total', 'Contacto URL'])
        profile = pd.concat([profile, ser.to_frame().T], ignore_index=True)

        print('Se agrega info de anuncio')

# Cerrar el navegador
driver.quit()

# Guardar los datos en un archivo Excel
filename = 'datos_inmuebles_arriendo.xlsx'
profile.to_excel(filename, index=False)
