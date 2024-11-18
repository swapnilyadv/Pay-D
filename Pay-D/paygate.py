import streamlit as st
import razorpay

def payment_gateway():
    st.title("Payment Gateway")
    
    # Initialize Razorpay client
    # Replace with your actual Razorpay key_id and key_secret
    razorpay_client = razorpay.Client(auth=("rzp_test_YOUR_KEY_ID", "YOUR_KEY_SECRET"))
    
    # Payment form
    st.write("Enter Payment Details")
    amount = st.number_input("Amount (in INR)", min_value=1, value=100)
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    contact = st.text_input("Contact Number")
    
    if st.button("Pay Now"):
        try:
            # Create Razorpay order
            payment_order = razorpay_client.order.create({
                'amount': amount * 100,  # Amount in paise
                'currency': 'INR',
                'payment_capture': '1'
            })
            
            # Generate payment button
            st.write("Please complete your payment")
            options = {
                "key": "rzp_test_C7MBtYxYsTybtZ",
                "amount": amount * 100,
                "currency": "INR",
                "name": "Pay-D",
                "description": "Payment for services",
                "order_id": payment_order['id'],
                "prefill": {
                    "name": name,
                    "email": email,
                    "contact": contact
                },
            }
            
            # Display payment button using HTML
            html = f"""
            <form action="/payment/success/" method="POST">
                <script
                    src="https://checkout.razorpay.com/v1/checkout.js"
                    data-key="{options['key']}"
                    data-amount="{options['amount']}"
                    data-currency="{options['currency']}"
                    data-order_id="{options['order_id']}"
                    data-name="{options['name']}"
                    data-description="{options['description']}"
                    data-prefill.name="{options['prefill']['name']}"
                    data-prefill.email="{options['prefill']['email']}"
                    data-prefill.contact="{options['prefill']['contact']}"
                >
                </script>
            </form>
            """
            st.components.v1.html(html, height=50)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    payment_gateway()
