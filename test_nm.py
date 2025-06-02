import allure
from playwright.sync_api import sync_playwright
import random

def generate_random_email():
    return f"user{random.randint(1000,9999)}@example.com"

@allure.title("Test Add Business Owner")
def test_add_business_owner():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://dashboard.impactoapps.com/business-owners")

        print("Clicking 'Add Business Owner' button...")
        page.click("button:has-text('Add Business Owner')")
        page.wait_for_timeout(1000)  # wait for modal animation

        try:
            page.wait_for_selector("h5:has-text('Add Business Owner')", timeout=5000)
        except:
            page.wait_for_selector("text=Add Business Owner", timeout=5000)
        print("Modal appeared!")

        page.fill("#name", "Automation User")
        page.fill("#email", generate_random_email())
        page.fill("#countryDialCode", "+880")
        page.fill("#phone", "01712345678")
        page.fill("#dateOfBirth", "1990-01-01")

        # Gender dropdown (Ant Design style)
        page.click("#gender")
        page.wait_for_timeout(1000)  # wait for dropdown options
        page.locator("div[role='option']:has-text('Male')").click()

        page.fill("#location", "Dhaka")
        page.fill("#password", "StrongPass123!")

        # Role dropdown
        page.click("#role")
        page.wait_for_timeout(1000)
        page.locator("div[role='option']:has-text('business')").click()

        page.fill("#companyAddress", "123 Automation St.")
        page.fill("#companyName", "Automation Company")

        subscribed_checkbox = page.locator("input[type='checkbox'][aria-label='Is Subscribed']")
        if subscribed_checkbox.count() > 0 and not subscribed_checkbox.is_checked():
            subscribed_checkbox.check()     

        page.fill("#freeDownloads", "10")
        page.fill("#freeUploads", "20")

        # File uploads - update with actual paths on your machine
        page.set_input_files("input#pictureUpload", r"C:\path\to\sample_picture.jpg")
        page.set_input_files("input#idProofUpload", r"C:\path\to\sample_idproof.pdf")
        page.set_input_files("input#verificationIdUpload", r"C:\path\to\sample_verificationid.pdf")

        page.click("button:has-text('Submit')")

        page.wait_for_timeout(5000)
        print("New Business Owner added successfully!")

        browser.close()
