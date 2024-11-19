from playwright.sync_api import sync_playwright, expect
import time
from datetime import datetime, timedelta

def run_tests():
    with sync_playwright() as p:
        # Initialize the browser and create a new page
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print("\n--- Starting Historical Weather Page Tests ---")

            # Test 1: Navigate to the historical weather page
            print("\nTest 1: Navigating to the historical weather page")
            page.goto("http://localhost:5000/historical_weather")  
            
            # Test 2: Check if the page title is correct
            print("\nTest 2: Checking if the page title is correct")
            expect(page).to_have_title("Historical Weather")
            print("Page title is correct")  
            
            # Test 3: Check if the location input field is present
            print("\nTest 3: Checking if the location input field is present")
            location_input = page.locator('#location')
            expect(location_input).to_be_visible()
            print("Location input field is visible")
            
            # Test 4: Check if date pickers are present
            print("\nTest 4: Checking if date pickers are present")
            start_date_picker = page.locator('#startDate')
            end_date_picker = page.locator('#endDate')
            expect(start_date_picker).to_be_visible()
            expect(end_date_picker).to_be_visible()
            print("Date pickers are visible")
            
            # Test 5: Test search functionality
            print("\nTest 5: Testing search functionality")
            location_input.fill("London")
            page.click('#fetchData')
            
            # Wait for the location name to update
            print("Waiting for location name to update")
            page.wait_for_function('''
                    () => document.querySelector('#locationName').textContent.trim() !== 'Loading...'
                ''', timeout=5000)

            location_name = page.inner_text('#locationName')
            print(f"Location name updated to: {location_name}")
            assert "London" in location_name, f"Expected London, got {location_name}"
            print("Search functionality test passed")
            
            # Test 6: Check if the table is populated with data
            print("\nTest 6: Checking if the table is populated")
            page.wait_for_selector('#forecastWeatherTable tr')
            rows = page.query_selector_all('#forecastWeatherTable tr')
            print(f"Number of rows in the table: {len(rows)}")
            assert len(rows) > 0, "Weather data table is empty"
            print("Table population test passed")
            
            # Test 7: Test date picker functionality
            print("\nTest 7: Testing date picker functionality")
            today = datetime.now()
            week_ago = today - timedelta(days=7)
            start_date = week_ago.strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
            
            print(f"Setting date range: {start_date} to {end_date}")
            start_date_picker.fill(start_date)
            end_date_picker.fill(end_date)
            page.click('#fetchData')
            
            # Wait for the table to update after changing dates
            print("Waiting for table to update")
            page.wait_for_timeout(2000)  # Wait for 2 seconds
            
            # Test 8: Verify the date range in the table
            print("\nTest 8: Verifying date range in the table")
            first_date = page.locator('#forecastWeatherTable tr:first-child td:first-child').inner_text()
            last_date = page.locator('#forecastWeatherTable tr:last-child td:first-child').inner_text()
            print(f"First date in table: {first_date}, Last date in table: {last_date}")
            assert first_date == start_date, f"First date {first_date} is before start date {start_date}"
            assert last_date == end_date, f"Last date {last_date} is after end date {end_date}"
            print("Date range verification passed")
            
            # Test 9: Test 'View Details' functionality
            print("\nTest 9: Testing 'View Details' functionality")
            page.click('.view-details:first-child')
            page.wait_for_selector('#weatherDetailsModal')
            modal_title = page.inner_text('#weatherDetailsModalLabel')
            print(f"Modal title: {modal_title}")
            assert "Weather Details for" in modal_title, f"Unexpected modal title: {modal_title}"
            print("'View Details' functionality test passed")
            
            # Test 10: Check modal content
            print("\nTest 10: Checking modal content")
            modal_content = page.inner_text('#weatherDetailsModalContent')
            print(f"Modal content preview: {modal_content[:500]}...")  # Print first 500 characters
            expect(page.locator('#weatherDetailsModalContent')).to_contain_text("Day Overview")
            expect(page.locator('#weatherDetailsModalContent')).to_contain_text("Hourly Forecast")
            print("Modal content check passed")
            
            # Test 11: Test modal close functionality
            print("\nTest 11: Testing modal close functionality")
            page.click('.modal .close')
            page.wait_for_selector('#weatherDetailsModal', state='hidden')
            print("Modal close test passed")
            
            print("\n--- All tests passed successfully! ---")
            
        except AssertionError as e:
            # Handle assertion errors (test failures)
            print(f"\nTest failed: {str(e)}")
            page.screenshot(path="error_screenshot.png")
            print("Error screenshot saved as error_screenshot.png")
        except Exception as e:
            # Handle other exceptions
            print(f"\nAn error occurred: {str(e)}")
            page.screenshot(path="error_screenshot.png")
            print("Error screenshot saved as error_screenshot.png")
        finally:
            # Ensure the browser is closed even if tests fail
            print("\nClosing browser")
            browser.close()

if __name__ == "__main__":
    print("Starting test run for Historical Weather Page")
    run_tests()
    print("Test run completed")