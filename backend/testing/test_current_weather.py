from playwright.sync_api import sync_playwright, expect
import time
import json

def run_tests():
    with sync_playwright() as p:
            try:
                # Initialize the browser and create a new page
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                
                # Test 1: Check if the current weather page loads correctly
                print("\n1. Testing current weather page...")
                start_time = time.time()
                page.goto("http://localhost:5000/")
                page.wait_for_load_state('networkidle')
                assert "Current Weather" in page.title()
                assert "http://localhost:5000/" in page.url
                print("Current weather page loaded successfully.")
                
                # Test 2: Test the search functionality
                print("\n2. Testing search functionality...")
                page.fill('#location', 'London')
                page.click('#fetchData')

                # Wait for the location name to update
                page.wait_for_function('''
                    () => document.querySelector('#locationName').textContent.trim() !== 'Loading...'
                ''', timeout=5000)
                
                location_name = page.inner_text('#locationName')
                assert "London" in location_name, f"Expected London, got {location_name}"
                print(f"Search functionality working. Location name updated to: {location_name}")
                
                # Test 3: Test error handling for invalid search
                print("\n3. Testing search error handling...")
                page.fill('#location', '!@#$%^')
                page.click('#fetchData')

                # Wait for the error message to appear
                page.wait_for_function('''
                    () => {
                        const locationName = document.querySelector('#locationName');
                        return locationName && 
                            (locationName.textContent.trim() !== 'Loading...' &&
                                locationName.textContent.trim() !== 'London');
                    }
                ''', timeout=5000)

                error_message = page.inner_text('#locationName')
                assert "Enter a valid city or country name." in error_message, f"Expected: Enter a valid city or country name., got: {error_message}"
                print(f"Error handling working. Error message: {error_message}")
                
                # Test 4: Check if weather data is loaded
                print("\n4. Testing data loading...")
                page.wait_for_function('''
                    () => {
                        return document.querySelectorAll('#forecastWeatherTable tr').length >= 1 &&
                            document.querySelectorAll('#forecastHourlyTable tr').length >= 1;
                    }
                ''', timeout=5000)
                print("Data loaded successfully.")
                
                # Test 5: Test the current weather API endpoint
                print("\n5. Testing current weather API endpoint...")
                start_time = time.time()
                response = page.request.post("http://localhost:5000/api/weather", 
                                            data='{"location": "London", "dataType": "current", "days" : "1"}',
                                            headers={"Content-Type": "application/json"})
                assert response.ok
                json_response = response.json()
                assert 'current' in json_response
                assert 'location' in json_response
                assert len(json_response) == 2, f"Expected : 2, got {len(json_response)}"
                print(f"Current weather API endpoint test passed. Time taken: {time.time() - start_time:.2f} seconds")
                
                # Test 6: Test the forecast weather API endpoint
                print("\n6. Testing forecast weather API endpoint...")
                start_time = time.time()
                response = page.request.post("http://localhost:5000/api/weather", 
                                            data='{"location": "London", "dataType": "forecast", "days" : "10"}',
                                            headers={"Content-Type": "application/json"})
                assert response.ok
                json_response = response.json()
                assert 'forecast' in json_response
                assert 'location' in json_response
                assert len(json_response['forecast']) == 10, f"Expected forecast: 10, got {len(json_response['forecast'])}"
                assert len(json_response['location']) == 8, f"Expected location: 8, got {len(json_response['location'])}"
                assert len(json_response) == 2, f"Expected : 2, got {len(json_response)}"
                print(f"Forecast weather API endpoint test passed. Time taken: {time.time() - start_time:.2f} seconds")
                
                # Test 7: Check if the forecast daily table is populated
                print("\n7. Testing forecast daily table...")
                forecast_rows = page.query_selector_all('#forecastWeatherTable tr')
                assert len(forecast_rows) >= 1, "Forecast daily table is empty"
                print(f"Forecast daily table populated with {len(forecast_rows)} rows.")
                
                # Test 8: Check if the forecast hourly table is populated
                print("\n8. Testing forecast hourly table...")
                hourly_rows = page.query_selector_all('#forecastHourlyTable tr')
                assert len(hourly_rows) == 24, f"Expected 24 rows, got {len(hourly_rows)}"
                print(f"Forecast hourly table populated with {len(hourly_rows)} rows.")
                
                # Test 9: Check if all charts are rendered
                print("\n9. Testing charts...")

                def check_chart_data(page, selector):
                    return page.evaluate(f'''
                        () => {{
                            const chart = document.querySelector('{selector}');
                            if (!chart) return false;    
                            const chartInstance = Chart.getChart(chart);
                            if (!chartInstance) return false;
                            const data = chartInstance.data;
                            return data && data.datasets && data.datasets.length > 0 && data.datasets[0].data && data.datasets[0].data.length > 0;
                        }}
                    ''')

                for chart_id in ['temperatureChart', 'barChartData', 'filledLineChart']:
                    chart_has_data = check_chart_data(page, f'#{chart_id}')
                    print(f"Chart {chart_id} : ",chart_has_data)
                    assert chart_has_data, f"Chart {chart_id} is not rendered properly or has no data"
                    print(f"Chart {chart_id} rendered successfully.")

                print("All charts rendered successfully.")
                
                # Test 10: Check if the map is rendered
                print("\n10. Testing map...")
                page.wait_for_selector('#map')
                map_element = page.query_selector('#map')
                assert map_element is not None, "Map not found"
                print("Map rendered successfully.")
                
                # Test 11: Test map interaction
                print("\n11. Testing map interaction...")
                page.click('#map')
                page.wait_for_selector('.leaflet-popup', timeout=5000)
                popup = page.query_selector('.leaflet-popup')
                assert popup is not None, "Map popup not displayed after click"
                print("Map interaction working. Popup displayed after click.")

                # Test 12: Test responsive design
                print("\n12. Testing responsive design...")
                page.set_viewport_size({"width": 375, "height": 667})  # Mobile size
                assert page.is_visible('#sidebarMenu'), "Mobile menu not visible on small screen"
                print("Mobile menu visible on small screen.")
                page.set_viewport_size({"width": 1920, "height": 1080})  # Desktop size
                assert not page.is_visible('#sidebarMenu'), "Mobile menu visible on large screen"
                print("Mobile menu not visible on large screen.")
                
                # Test 13: Test accessibility
                print("\n13. Testing accessibility...")
                accessibility = page.accessibility.snapshot()
                assert len(accessibility['children']) > 0, "No accessible elements found"
                print(f"Accessibility test passed. Found {len(accessibility['children'])} accessible elements.")
                
                # Test 14: Navigate to Historical dashboard page
                print("\n14. Testing navigation to Historical weather dashboard page...")
                # Assuming there's an "Historical Weather" link in the navigation
                page.click('text=Historical Weather') 
                page.wait_for_load_state('networkidle')

                # Check if we've navigated to the correct URL
                assert "historical_weather" in page.url.lower(), f"Expected 'historical_weather' in URL, but got: {page.url}"
                print("Historical dashboard is successfully navigated.")
                
                # Test 15: Navigate to Historical dashboard page
                print("\n15. Testing navigation to current weather dashboard page...")
                # Assuming there's an "Current Weather" link in the navigation
                page.click('text=Current Weather') 
                page.wait_for_load_state('networkidle')

                # Check if we've navigated to the correct URL
                assert "current_weather" in page.url.lower(), f"Expected 'current_weather' in URL, but got: {page.url}"
                print("Current dashboard is successfully navigated.")
                
                print(f"\nAll tests passed. Total time taken: {time.time() - start_time:.2f} seconds")

            except AssertionError as e:
                print(f"\nTest failed: {str(e)}")
                page.screenshot(path="error_screenshot.png")
                print("Error screenshot saved as error_screenshot.png")
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                page.screenshot(path="error_screenshot.png")
                print("Error screenshot saved as error_screenshot.png")
            finally:
                # Clean up: close the page and browser
                if page:
                    page.close()
                if browser:
                    browser.close()
                print("\nBrowser closed. Test run completed.")

if __name__ == "__main__":
    print("Starting test run for Current Weather Page")
    run_tests()
    print("Test run completed")