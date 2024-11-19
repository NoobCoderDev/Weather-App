from playwright.sync_api import sync_playwright, expect
import time

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Test the current weather page
            print("Testing current weather page...")
            start_time = time.time()
            page.goto("http://localhost:5000/current_weather")
            page.wait_for_load_state('networkidle')
            print(f"Page title: {page.title()}")
            assert "Current Weather" in page.title()
            print(f"Current weather page test passed. Time taken: {time.time() - start_time:.2f} seconds")

            # Test the historical weather page
            print("Testing historical weather page...")
            start_time = time.time()
            page.goto("http://localhost:5000/historical_weather")
            page.wait_for_load_state('networkidle')
            assert "Historical Weather" in page.title()
            print(f"Historical weather page test passed. Time taken: {time.time() - start_time:.2f} seconds")

            # Test the API endpoint
            print("Testing API endpoint...")
            start_time = time.time()
            response = page.request.post("http://localhost:5000/api/weather", 
                                         data='{"location": "London", "dataType": "current"}',
                                         headers={"Content-Type": "application/json"})
            assert response.ok
            json_response = response.json()
            assert 'current' in json_response
            assert 'location' in json_response
            print(f"API endpoint test passed. Time taken: {time.time() - start_time:.2f} seconds")

        except AssertionError as e:
            print(f"Test failed: {str(e)}")
            print(f"Current URL: {page.url}")
            print(f"Page content: {page.content()}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            browser.close()

if __name__ == "__main__":
    run_tests()