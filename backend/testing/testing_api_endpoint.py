from playwright.sync_api import sync_playwright, expect
import json
from datetime import datetime, timedelta

def run_tests():
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            base_url = "http://localhost:5000"
            
            print("\n--- Starting Weather API Tests ---")

            # Test 1: Current Weather Data
            print("\nTest 1: Testing Current Weather API")
            response = page.request.post(f"{base_url}/api/weather",
                data=json.dumps({
                    "location": "London",
                    "dataType": "current",
                    "days": 1
                }),
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            
            assert 'current' in result, "Response doesn't contain 'current' key"
            assert 'location' in result, "Response doesn't contain 'location' key"
            print("Current Weather API test passed")

            # Test 2: Forecast Weather Data
            print("\nTest 2: Testing Forecast Weather API")
            response = page.request.post(f"{base_url}/api/weather",
                data=json.dumps({
                    "location": "New York",
                    "dataType": "forecast",
                    "days": 3
                }),
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            
            assert 'forecast' in result, "Response doesn't contain 'forecast' key"
            assert 'location' in result, "Response doesn't contain 'location' key"
            assert len(result['forecast']) == 3, f"Expected 3 days of forecast, got {len(result['forecast'])}"
            print("Forecast Weather API test passed")

            # Test 3: Historical Weather Data
            print("\nTest 3: Testing Historical Weather API")
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
            response = page.request.post(f"{base_url}/api/weather",
                data=json.dumps({
                    "location": "Paris",
                    "dataType": "historical",
                    "startDate": start_date,
                    "endDate": end_date
                }),
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            
            assert 'historical' in result, "Response doesn't contain 'historical' key"
            assert 'location' in result, "Response doesn't contain 'location' key"
            assert len(result['historical']) == 3, f"Expected 3 days of historical data, got {len(result['historical'])}"
            print("Historical Weather API test passed")

            # Test 4: Current Location Weather Data
            print("\nTest 4: Testing Current Location Weather API")
            response = page.request.get(f"{base_url}/get_weather?lat=51.5074&lon=-0.1278")
            result = response.json()
            
            assert 'current' in result, "Response doesn't contain 'current' key"
            assert 'location' in result, "Response doesn't contain 'location' key"
            assert result['location']['name'] == 'London', f"Expected London, got {result['location']['name']}"
            print("Current Location Weather API test passed")

            print("\n--- All tests passed successfully! ---")
            
        except AssertionError as e:
            print(f"\nTest failed: {str(e)}")
            page.screenshot(path="error_screenshot.png")
            print("Error screenshot saved as error_screenshot.png")
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            page.screenshot(path="error_screenshot.png")
            print("Error screenshot saved as error_screenshot.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run_tests()