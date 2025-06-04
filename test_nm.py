import pytest
import allure
from playwright.sync_api import sync_playwright
import random
import time
from datetime import datetime

# Login credentials
LOGIN_CREDENTIALS = {
    "email": "admin@gmail.com",
    "password": "123@321"
}

# URLs
URLS = {
    "login": "https://dashboard.impactoapps.com/auth/login",
    "dashboard": "https://dashboard.impactoapps.com/",
    "business_owners": "https://dashboard.impactoapps.com/business-owners"
}

def generate_random_email():
    """Generate a unique email for testing"""
    timestamp = int(time.time())
    random_num = random.randint(100, 999)
    return f"testuser{timestamp}{random_num}@example.com"

def generate_random_phone():
    """Generate a random Bangladesh phone number"""
    return f"017{random.randint(10000000, 99999999)}"

def login_to_dashboard(page):
    """
    Login to the dashboard with provided credentials
    """
    with allure.step(" Login to Dashboard"):
        # Navigate to login page
        page.goto(URLS["login"], timeout=30000)
        page.wait_for_load_state("networkidle")
        
        # Wait for login form
        page.wait_for_selector("#email", timeout=15000)
        allure.attach(page.screenshot(), name=" Login Page", attachment_type=allure.attachment_type.PNG)
        
        # Fill credentials
        page.fill("#email", LOGIN_CREDENTIALS["email"])
        page.wait_for_timeout(500)
        page.fill("#password", LOGIN_CREDENTIALS["password"])
        page.wait_for_timeout(500)
        
        # Take screenshot before login
        allure.attach(page.screenshot(), name=" Credentials Filled", attachment_type=allure.attachment_type.PNG)
        
        # Find and click login button
        login_button = page.locator("button[type='submit'], button:has-text('Login'), button:has-text('Sign In')")
        if login_button.count() > 0:
            login_button.first.click()
        else:
            # Try alternative selectors
            page.locator("form").press("Enter")
        
        # Wait for login to complete
        page.wait_for_timeout(3000)
        
        # Verify login success by checking URL or dashboard elements
        try:
            # Wait for redirect to dashboard or check for dashboard elements
            page.wait_for_url(URLS["dashboard"], timeout=10000)
        except:
            # Alternative: check if we're no longer on login page
            current_url = page.url
            if "login" not in current_url:
                print(" Login successful - redirected from login page")
            else:
                # Check for error messages
                error_elements = page.locator(".ant-message-error, .error, [class*='error']")
                if error_elements.count() > 0:
                    error_text = error_elements.first.text_content()
                    raise Exception(f"Login failed with error: {error_text}")
        
        allure.attach(page.screenshot(), name=" After Login", attachment_type=allure.attachment_type.PNG)
        allure.attach(f"Logged in as: {LOGIN_CREDENTIALS['email']}", name=" Login Success", attachment_type=allure.attachment_type.TEXT)
        print(f" Successfully logged in as: {LOGIN_CREDENTIALS['email']}")

@allure.epic("Business Owner Management")
@allure.feature("Add Business Owner")
@allure.story("Create New Business Owner with Authentication")
@allure.title(" CREATE NEW BUSINESS OWNER - FULL WORKFLOW")
@allure.description("Complete test that logs in and creates a new business owner with all required fields")
@allure.severity(allure.severity_level.lower)
def test_create_business_owner_with_login():
    """
    MAIN TEST: Login and create a new business owner
    """
    
    with sync_playwright() as p:
        # Launch browser with visible mode for debugging
        browser = p.chromium.launch(headless=False, slow_mo=800)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        try:
            # Step 1: Login to the dashboard
            login_to_dashboard(page)
            
            # Step 2: Navigate to Business Owners page
            with allure.step(" Navigate to Business Owners"):
                page.goto(URLS["business_owners"], timeout=30000)
                page.wait_for_load_state("networkidle")
                allure.attach(page.screenshot(), name=" Business Owners Page", attachment_type=allure.attachment_type.PNG)
                print(" Successfully navigated to Business Owners page")
                
            # Step 3: Click Add Business Owner button
            with allure.step(" Open Add Business Owner Form"):
                add_button = page.locator("button:has-text('Add Business Owner'), button:has-text('Add')")
                if add_button.count() > 0:
                    add_button.first.click()
                else:
                    # Try alternative selectors
                    page.locator("[data-testid*='add'], .add-button, button[class*='add']").first.click()
                
                page.wait_for_timeout(3000)
                
                # Wait for modal to appear
                modal_selectors = [
                    "text=Add Business Owner",
                    ".ant-modal",
                    "[role='dialog']",
                    ".modal"
                ]
                
                modal_found = False
                for selector in modal_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        modal_found = True
                        break
                    except:
                        continue
                
                if not modal_found:
                    allure.attach(page.screenshot(), name=" No Modal Found", attachment_type=allure.attachment_type.PNG)
                    raise Exception("Add Business Owner modal did not appear")
                
                allure.attach(page.screenshot(), name=" Add Business Owner Modal", attachment_type=allure.attachment_type.PNG)
                print(" Add Business Owner modal opened")
                
            # Step 4: Generate test data
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_email = generate_random_email()
            test_phone = generate_random_phone()
            
            test_data = {
                "name": f"TestUser_{current_time}",
                "email": test_email,
                "countryDialCode": "+880",
                "phone": test_phone,
                "dateOfBirth": "1990-01-01",
                "location": "Dhaka, Bangladesh",
                "password": "TestPass123!",
                "companyAddress": f"123 Test Street, Dhaka-{current_time}",
                "companyName": f"TestCompany_{current_time}",
                "free_downloads": "20",
                "free_uploads": "30"
            }
            
            # Log test data
            test_data_text = " GENERATED TEST DATA:\n" + "\n".join([f"  • {k}: {v}" for k, v in test_data.items()])
            allure.attach(test_data_text, name=" Test Data", attachment_type=allure.attachment_type.TEXT)
            print(f" Generated test data for: {test_data['name']}")
            
            # Step 5: Fill form fields
            with allure.step(" Fill Basic Information"):
                # Fill basic fields with error handling
                fields_to_fill = [
                    ("name", test_data["name"]),
                    ("email", test_data["email"]),
                    ("countryDialCode", test_data["countryDialCode"]),
                    ("phone", test_data["phone"]),
                    ("dateOfBirth", test_data["dateOfBirth"])
                ]
                
                for field_id, value in fields_to_fill:
                    try:
                        field_selector = f"#{field_id}"
                        if page.locator(field_selector).count() > 0:
                            page.fill(field_selector, value)
                            page.wait_for_timeout(500)
                            print(f" Filled {field_id}: {value}")
                        else:
                            print(f"Field {field_id} not found")
                    except Exception as e:
                        print(f" Error filling {field_id}: {e}")
                
                allure.attach(page.screenshot(), name=" Basic Info Filled", attachment_type=allure.attachment_type.PNG)
                
            with allure.step(" Select Gender"):
                try:
                    # Multiple strategies to find and select gender field
                    gender_selectors = [
                        "#gender",
                        "[name='gender']", 
                        "select[id*='gender']",
                        ".ant-select:has([placeholder*='gender' i])",
                       ".ant-select:has([placeholder*='Gender'])",
                        "div:has(label:text('Gender')) .ant-select",
                        "[data-testid*='gender']"
                    ]
                    
                    gender_field = None
                    for selector in gender_selectors:
                        if page.locator(selector).count() > 0:
                            gender_field = page.locator(selector).first
                            print(f"Found gender field using: {selector}")
                            break
                    
                    if gender_field:
                        # Click to open dropdown
                        gender_field.click()
                        page.wait_for_timeout(150)
                        
                        # Take screenshot of opened dropdown
                        allure.attach(page.screenshot(), name=" Gender Dropdown Opened", attachment_type=allure.attachment_type.PNG)
                        
                        # Multiple strategies to select gender option
                        gender_selected = False
                        
                        # Strategy 1: Look for specific gender options
                        gender_option_selectors = [
                            '[role="option"]:has-text("Male")',
                           # '[role="option"]:has-text("Female")',
                            'option:has-text("Male")',
                           # 'option:has-text("Female")',
                            '.ant-select-item:has-text("Male")',
                            #'.ant-select-item:has-text("Female")',
                            'li:has-text("Male")',
                           # 'li:has-text("Female")'
                        ]
                        
                        for selector in gender_option_selectors:
                            try:
                                options = page.locator(selector)
                                if options.count() > 0:
                                    options.first.click()
                                    gender_selected = True
                                    selected_text = options.first.text_content()
                                    print(f" Selected gender: {selected_text}")
                                    break
                            except:
                                continue
                        
                        # Strategy 2: Select first available option
                        if not gender_selected:
                            option_selectors = [
                                '[role="option"]',
                                '.ant-select-item',
                                '.ant-select-item-option',
                                'option',
                                'li[data-value]'
                            ]
                            
                            for selector in option_selectors:
                                try:
                                    options = page.locator(selector)
                                    if options.count() > 0:
                                        options.first.click()
                                        gender_selected = True
                                        print(" Selected first available gender option")
                                        break
                                except:
                                    continue
                        
                        # Strategy 3: Keyboard navigation
                        if not gender_selected:
                            try:
                                page.keyboard.press("ArrowDown")
                                page.wait_for_timeout(500)
                                page.keyboard.press("Enter")
                                gender_selected = True
                                print(" Selected gender using keyboard navigation")
                            except:
                                pass
                        
                        # Strategy 4: Try clicking on dropdown items
                        if not gender_selected:
                            try:
                                # Look for any clickable items in dropdown
                                dropdown_items = page.locator(".ant-select-dropdown .ant-select-item, .dropdown-item, [role='listbox'] > *")
                                if dropdown_items.count() > 0:
                                    dropdown_items.first.click()
                                    gender_selected = True
                                    print(" Selected gender using dropdown item click")
                            except:
                                pass
                        
                        page.wait_for_timeout(1000)
                        
                        if gender_selected:
                            allure.attach("Gender selection successful", name=" Gender Selected", attachment_type=allure.attachment_type.TEXT)
                        else:
                            allure.attach("Gender selection failed - continuing with test", name=" Gender Selection", attachment_type=allure.attachment_type.TEXT)
                            print(" Could not select gender - continuing with test")
                    else:
                        print(" Gender field not found - might be optional")
                        allure.attach("Gender field not found", name=" Gender Field", attachment_type=allure.attachment_type.TEXT)
                        
                except Exception as e:
                    print(f" Gender selection error: {e}")
                    allure.attach(f"Gender selection error: {e}", name=" Gender Error", attachment_type=allure.attachment_type.TEXT)
                
                # Take final screenshot after gender selection attempt
                allure.attach(page.screenshot(), name=" After Gender Selection", attachment_type=allure.attachment_type.PNG)
                
            with allure.step(" Fill Company Information"):
                company_fields = [
                    ("location", test_data["location"]),
                    ("password", test_data["password"]),
                    ("companyAddress", test_data["companyAddress"]),
                    ("companyName", test_data["companyName"])
                ]
                
                for field_id, value in company_fields:
                    try:
                        field_selector = f"#{field_id}"
                        if page.locator(field_selector).count() > 0:
                            page.fill(field_selector, value)
                            page.wait_for_timeout(500)
                            print(f" Filled {field_id}")
                    except Exception as e:
                        print(f" Error filling {field_id}: {e}")
                
                allure.attach(page.screenshot(), name=" Company Info Filled", attachment_type=allure.attachment_type.PNG)
                
            with allure.step(" Fill Download/Upload Limits"):
                try:
                    if page.locator("#free_downloads").count() > 0:
                        page.fill("#free_downloads", test_data["free_downloads"])
                        print(" Filled free downloads")
                except Exception as e:
                    print(f" Free downloads: {e}")
                
                try:
                    if page.locator("#free_uploads").count() > 0:
                        page.fill("#free_uploads", test_data["free_uploads"])
                        print(" Filled free uploads")
                except Exception as e:
                    print(f" Free uploads: {e}")
                    
            with allure.step(" Handle Checkboxes"):
                try:
                    checkboxes = page.locator("input[type='checkbox']")
                    if checkboxes.count() > 0:
                        for i in range(checkboxes.count()):
                            if not checkboxes.nth(i).is_checked():
                                checkboxes.nth(i).check()
                        print(" Checked subscription checkbox(es)")
                except Exception as e:
                    print(f" Checkbox handling: {e}")
                    
            # Step 6: Validate and submit form
            with allure.step(" Validate Form Before Submission"):
                allure.attach(page.screenshot(), name=" Form Ready for Submission", attachment_type=allure.attachment_type.PNG)
                
                # Validate form fields
                validation_script = """
                    () => {
                        const fields = ['name', 'email', 'countryDialCode', 'phone', 'dateOfBirth', 
                                      'location', 'password', 'companyAddress', 'companyName'];
                        const results = {};
                        fields.forEach(field => {
                            const element = document.querySelector(`#${field}`);
                            const value = element ? element.value.trim() : '';
                            results[field] = {filled: value.length > 0, value: value};
                        });
                        return results;
                    }
                """
                
                field_status = page.evaluate(validation_script)
                
                validation_report = " FORM VALIDATION REPORT:\n"
                all_required_filled = True
                for field, info in field_status.items():
                    status = "" if info['filled'] else ""
                    validation_report += f"  {status} {field}: {info['value'][:30]}{'...' if len(info['value']) > 30 else ''}\n"
                    if not info['filled']:
                        all_required_filled = False
                
                allure.attach(validation_report, name=" Validation Report", attachment_type=allure.attachment_type.TEXT)
                print(" Form validation completed")
                
            with allure.step(" SUBMIT THE FORM"):
                print(" SUBMITTING FORM TO CREATE BUSINESS OWNER...")
                
                # Find submit button with multiple selectors
                submit_selectors = [
                    "button:has-text('Submit')",
                    "button:has-text('Create')",
                    "button[type='submit']",
                    ".ant-btn-primary",
                    "button:has-text('Save')"
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    buttons = page.locator(selector)
                    if buttons.count() > 0:
                        submit_button = buttons.first
                        break
                
                if submit_button:
                    submit_button.click()
                    print(" Submit button clicked!")
                    
                    # Wait for submission to process
                    page.wait_for_timeout(5000)
                    
                    # Take screenshot after submission
                    allure.attach(page.screenshot(), name=" After Form Submission", attachment_type=allure.attachment_type.PNG)
                    
                    # Check for success/error messages
                    success_indicators = [
                        ".ant-message-success",
                        ".success",
                        "[class*='success']",
                        "text=created successfully",
                        "text=added successfully"
                    ]
                    
                    error_indicators = [
                        ".ant-message-error",
                        ".error",
                        "[class*='error']",
                        "text=error",
                        "text=failed"
                    ]
                    
                    success_found = False
                    error_found = False
                    
                    for selector in success_indicators:
                        if page.locator(selector).count() > 0:
                            success_message = page.locator(selector).first.text_content()
                            allure.attach(f"Success: {success_message}", name=" Success Message", attachment_type=allure.attachment_type.TEXT)
                            success_found = True
                            break
                    
                    for selector in error_indicators:
                        if page.locator(selector).count() > 0:
                            error_message = page.locator(selector).first.text_content()
                            allure.attach(f"Error: {error_message}", name=" Error Message", attachment_type=allure.attachment_type.TEXT)
                            error_found = True
                            break
                    
                    # Get current page state
                    current_url = page.url
                    page_title = page.title()
                    
                    submission_info = f"""
BUSINESS OWNER CREATION COMPLETED!

Email: {test_data['email']}
 Name: {test_data['name']}  
 Company: {test_data['companyName']}📱 Phone: {test_data['phone']}
Current URL: {current_url}
 Page Title: {page_title}
 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Success Detected: {success_found}
 Error Detected: {error_found}
                    """
                    
                    allure.attach(submission_info, name=" Submission Results", attachment_type=allure.attachment_type.TEXT)
                    print(submission_info)
                    
                    # If modal closed or URL changed, likely successful
                    if "business-owners" in current_url and not page.locator(".ant-modal").is_visible():
                        print(" SUCCESS: Business owner likely created successfully!")
                    
                else:
                    error_msg = " Submit button not found!"
                    print(error_msg)
                    allure.attach(error_msg, name=" Error", attachment_type=allure.attachment_type.TEXT)
                    allure.attach(page.screenshot(), name=" No Submit Button", attachment_type=allure.attachment_type.PNG)
                    
        except Exception as e:
            error_info = f" TEST FAILED: {str(e)}"
            print(error_info)
            allure.attach(page.screenshot(), name=" Error Screenshot", attachment_type=allure.attachment_type.PNG)
            allure.attach(error_info, name=" Error Details", attachment_type=allure.attachment_type.TEXT)
            raise
        
        finally:
            print(" Closing browser...")
            page.wait_for_timeout(3000)  # Give time to see results
            browser.close()


@allure.epic("Business Owner Management")
@allure.feature("Authentication Test")
@allure.story("Login Verification")
@allure.title(" LOGIN TEST - Verify Authentication")
@allure.description("Test to verify login functionality works correctly")
@allure.severity(allure.severity_level.CRITICAL)
def test_login_only():
    """
    Test login functionality only
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            login_to_dashboard(page)
            
            # Verify we're logged in by checking dashboard elements
            with allure.step(" Verify Dashboard Access"):
                page.wait_for_timeout(3000)
                current_url = page.url
                
                if "dashboard" in current_url or "login" not in current_url:
                    print(" Login test passed!")
                    allure.attach("Login successful", name=" Success", attachment_type=allure.attachment_type.TEXT)
                else:
                    raise Exception("Login verification failed")
                    
        finally:
            browser.close()


@allure.epic("Business Owner Management")
@allure.feature("Form Inspection")
@allure.story("Debug Information")
@allure.title(" DEBUG - Inspect Form Fields")
@allure.description("Debug test to examine all form fields and their properties after login")
def test_debug_form_fields_with_login():
    """
    Debug test to inspect form fields after proper login
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Login first
            login_to_dashboard(page)
            
            with allure.step(" Open Business Owner Form"):
                page.goto(URLS["business_owners"])
                page.wait_for_timeout(2000)
                
                # Click add button
                add_button = page.locator("button:has-text('Add Business Owner'), button:has-text('Add')")
                if add_button.count() > 0:
                    add_button.first.click()
                else:
                    page.locator("[data-testid*='add'], .add-button").first.click()
                
                page.wait_for_timeout(3000)
                
            with allure.step(" Analyze Form Fields"):
                form_analysis = page.evaluate("""
                    () => {
                        const inputs = document.querySelectorAll('input, select, textarea');
                        const analysis = {
                            total_fields: inputs.length,
                            fields: [id. submit ']
                        };
                        
                        inputs.forEach((input, index) => {
                            analysis.fields.push({
                                index: index + 1,
                                id: input.id || 'no-id', gf id 
                                name: input.name || 'no-name',
                                type: input.type || input.tagName.toLowerCase(),
                                placeholder: input.placeholder || 'no-placeholder',
                                required: input.required,
                                visible: input.offsetParent !== null,
                                value: input.value || ''
                            });
                        });
                        
                        return analysis;
                    }
                """)
                
                # Create detailed report
                debug_report = f"""
 FORM FIELDS DEBUG REPORT (AUTHENTICATED)
=============================================
 Total Fields Found: {form_analysis['total_fields']}  #gdf yt ieg ("new id submit " )
 FIELD DETAILS:
"""
                
                for field in form_analysis['fields']:
                    visibility = "" if field['visible'] else ""
                    required = "" if field['required'] else "  "
                    debug_report += f"""
{field['index']:2d}. {visibility} {required} ID: {field['id']:20} | Type: {field['type']:10}
      Placeholder: {field['placeholder']}
      Current Value: {field['value'][:50]}{'...' if len(field['value']) > 50 else ''}
"""
                
                allure.attach(debug_report, name=" Form Analysis Report", attachment_type=allure.attachment_type.TEXT)
                allure.attach(page.screenshot(), name=" Form Fields Screenshot", attachment_type=allure.attachment_type.PNG)
                
                print(f" Found {form_analysis['total_fields']} form fields after login")
                
        finally:
            browser.close()


if __name__ == "__main__":
    print(" Starting Business Owner Tests with Authentication... YPI")
    print(" Available tests:")
    print("  1. test_login_only - Test login functionality")
    print("  2. test_create_business_owner_with_login - Full workflow test")
    print("  3. test_debug_form_fields_with_login - Debug form fields")
    print("\n Run with: pytest test_business_owner.py --alluredir=allure-results -v -s")
    print(" Generate report: allure serve allure-results")
