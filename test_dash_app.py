import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

@pytest.fixture
def driver():
    """Fixture to set up and tear down Chrome WebDriver"""
    # Setup Chrome driver with automatic ChromeDriver management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(10)
    yield driver
    # Teardown
    driver.quit()

def test_home_page_loads(driver):
    """Test 1: Verify home page loads with dashboard button"""
    # Navigate to the app
    driver.get('http://localhost:8050')
    
    # Find the dashboard button
    dashboard_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "dashboard-button"))
    )
    
    # Assert the button exists and has correct text
    assert dashboard_button.is_displayed()
    assert dashboard_button.text == "Go to Dashboard"

def test_navigation_to_dashboard(driver):
    """Test 2: Verify navigation from home to dashboard works"""
    # Start at home page
    driver.get('http://localhost:8050')
    
    # Click dashboard button
    dashboard_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "dashboard-button"))
    )
    dashboard_button.click()
    
    # Verify we're on dashboard page by checking for nav menu
    nav_menu = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "nav-menu"))
    )
    assert nav_menu.is_displayed()

def test_trend_comparison_dropdown(driver):
    """Test 3: Verify trend comparison dropdown functionality"""
    # Go directly to dashboard
    driver.get('http://localhost:8050/dashboard')
    
    # Wait for and find the dropdown
    dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "trend-metric"))
    )
    
    # Scroll element into view and wait for it to be clickable
    driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
    time.sleep(2)  # Wait for scroll to complete
    
    # Try to click using JavaScript if normal click fails
    try:
        dropdown.click()
    except:
        driver.execute_script("arguments[0].click();", dropdown)
    
    # Check if all options are present
    expected_options = ['Gender Gap', 'Regional Variance', 'London vs National']
    for option in expected_options:
        option_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{option}')]"))
        )
        assert option_element.is_displayed()

def test_charts_loading(driver):
    """Test 4: Verify all charts load on dashboard"""
    driver.get('http://localhost:8050/dashboard')
    
    # Add wait for page load
    time.sleep(2)  # Allow time for charts to render
    
    chart_ids = [
        'gender-unemployment-chart',
        'regional-unemployment-chart',
        'london-unemployment-chart',
        'trend-comparison-chart'
    ]
    
    for chart_id in chart_ids:
        chart = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, chart_id))
        )
        # Scroll each chart into view before checking
        driver.execute_script("arguments[0].scrollIntoView(true);", chart)
        time.sleep(1)  # Allow time for scroll
        assert chart.is_displayed() 