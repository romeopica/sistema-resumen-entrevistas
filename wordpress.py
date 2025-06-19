def crear_post(site_url, username, password, html):
    import requests
    from requests.auth import HTTPBasicAuth
    from nicegui import ui

    api_endpoint = f"{site_url}/wp-json/wp/v2/posts"
    new_post = { "content": html, "status": "publish" }

    try:
        response = requests.post(api_endpoint, json=new_post, auth=HTTPBasicAuth(username, password))
        if response.status_code == 201:
            post_url = response.json().get("link", "Desconocida")
            ui.notify(f'¡Post creado con éxito! URL: {post_url}', type='positive')
            return post_url
        else:
            ui.notify(f'Error al crear el post: {response.status_code} - {response.reason}', type='negative')
            return None
    except Exception as e:
        ui.notify(f'Error al realizar la solicitud HTTP: {str(e)}', type='negative')
        return None