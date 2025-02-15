import asyncio
from playwright.async_api import async_playwright
import logging
import os
import requests
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

WEBSHARE_API_KEY = os.getenv("WEBSHARE_API_KEY")
PROXY_USERNAME = os.getenv("PROXY_USERNAME")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
WEBSHARE_API_URL = "https://proxy.webshare.io/api/proxy/list/"

async def get_proxies():
    """Fetch a list of proxies from Webshare"""
    try:
        headers = {
            "Authorization": f"Token {WEBSHARE_API_KEY}"
        }
        response = requests.get(WEBSHARE_API_URL, headers=headers)
        if response.status_code == 200:
            proxies = response.json().get('results', [])
            # Format proxies as ip:port
            formatted_proxies = [f"{proxy['proxy_address']}:{proxy['ports']['http']}" for proxy in proxies]
            return formatted_proxies
        else:
            logging.error(f"Failed to fetch proxies from Webshare: {response.status_code}")
            return []
    except Exception as e:
        logging.error(f"Error fetching proxies from Webshare: {str(e)}")
        return []

async def test_proxy(proxy_str: str) -> bool:
    """Test if a proxy is working"""
    try:
        proxy_parts = proxy_str.split(":")
        if len(proxy_parts) != 2:
            logging.warning(f"Invalid proxy format: {proxy_str}")
            return False
        
        ip, port = proxy_parts
        
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(proxy={
                    "server": f"http://{ip}:{port}",
                    "username": PROXY_USERNAME,
                    "password": PROXY_PASSWORD
                }, timeout=20000)
                page = await browser.new_page()
                await page.goto("https://www.example.com", timeout=10000)  # Shorter timeout
                await browser.close()
                return True
            except Exception as e:
                logging.warning(f"Proxy {proxy_str} failed: {str(e)}")
                if 'net::ERR_TUNNEL_CONNECTION_FAILED' in str(e):
                    logging.warning("Tunnel connection failed, likely a bad proxy.")
                return False
    except Exception as e:
        logging.warning(f"Error testing proxy {proxy_str}: {str(e)}")
        return False

async def generate_image_async(prompt: str, save_path: str) -> str:
    """Generate character image using Flux AI generator with proxy support and retry logic"""
    proxies = await get_proxies()
    
    # Test and filter proxies
    working_proxies = []
    for proxy_str in proxies:
        if await test_proxy(proxy_str):
            working_proxies.append(proxy_str)
    
    if not working_proxies:
        logging.warning("No working proxies available, running without proxy")
        proxy = None
    else:
        proxy_str = random.choice(working_proxies)
        logging.info(f"Using proxy: {proxy_str}")
        proxy_parts = proxy_str.split(":")
        proxy = {
            "server": f"http://{proxy_parts[0]}:{proxy_parts[1]}",
            "username": PROXY_USERNAME,
            "password": PROXY_PASSWORD
        }
    
    try:
        async with async_playwright() as p:
            launch_options = {"headless": True}  # Set to True for production
            if proxy:
                launch_options["proxy"] = proxy
            
            browser = await p.chromium.launch(**launch_options)
            page = await browser.new_page()
            
            # Navigate to Flux generator
            await page.goto("https://ai-girl.site/flux-ai-image-generator", timeout=30000)  # Increased timeout
            logging.info("Page loaded")
            
            # Enter prompt
            await page.fill('input[data-testid="textbox"]', prompt)
            logging.info(f"Entered prompt: {prompt}")
            
            # Start generation
            await page.click('button:has-text("Run")')
            logging.info("Started image generation")
            
            # Wait for generation (typical time ~15s)
            await page.wait_for_timeout(16000)
            
            # Look for the generated image with specific class pattern
            image_element = await page.wait_for_selector(
                'img.svelte-1pijsyv[src^="https://black-forest-labs-flux-1-schnell.hf.space/file=/tmp/gradio/"]',
                timeout=35000
            )
            
            if not image_element:
                raise Exception("Could not find generated image on the page")
            
            img_src = await image_element.get_attribute('src')
            logging.info(f"Found image: {img_src}")
            
            # Download image
            response = await page.request.get(img_src, timeout=30000)  # Increased timeout
            image_data = await response.body()
            
            # Save image
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(image_data)
            
            await browser.close()
            return save_path
            
    except Exception as e:
        logging.error(f"Error generating image: {str(e)}")
        return None

def generate_image(prompt: str, save_path: str) -> str:
    """Synchronous wrapper for generate_image_async"""
    return asyncio.get_event_loop().run_until_complete(
        generate_image_async(prompt, save_path)
    )
