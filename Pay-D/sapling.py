import streamlit as st
import pandas as pd
import razorpay

# Configure Streamlit page settings
st.set_page_config(
    page_title="Tree Shop",
    page_icon="🌳",
    layout="wide"
)

class TreeShop:
    def __init__(self):
        if 'cart' not in st.session_state:
            st.session_state.cart = []
        if 'razorpay_payment' not in st.session_state:
            st.session_state.razorpay_payment = None
            
        self.trees = [
            {"id": 1, "name": "Oak Tree", "price": 100, "height": "15-20m", "lifespan": "100+ years"},
            {"id": 2, "name": "Maple Tree", "price": 80, "height": "12-18m", "lifespan": "80+ years"},
            {"id": 3, "name": "Pine Tree", "price": 90, "height": "10-15m", "lifespan": "50+ years"},
            {"id": 4, "name": "Apple Tree", "price": 120, "height": "8-12m", "lifespan": "30+ years"},
            {"id": 5, "name": "Cherry Tree", "price": 150, "height": "6-10m", "lifespan": "25+ years"},
            {"id": 6, "name": "Birch Tree", "price": 85, "height": "15-25m", "lifespan": "40+ years"},
            {"id": 7, "name": "Willow Tree", "price": 130, "height": "20-25m", "lifespan": "60+ years"},
            {"id": 8, "name": "Palm Tree", "price": 200, "height": "15-30m", "lifespan": "70+ years"},
            {"id": 9, "name": "Eucalyptus Tree", "price": 110, "height": "30-55m", "lifespan": "50+ years"},
            {"id": 10, "name": "Cypress Tree", "price": 95, "height": "20-30m", "lifespan": "40+ years"}
        ]
        self.razorpay_client = razorpay.Client(auth=("your_api_key", "your_api_secret"))  # Replace with your Razorpay credentials

    def display_trees(self):
        st.header("Available Trees")
        for tree in self.trees:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            with col1:
                st.write(f"**{tree['name']}**")
                st.write(f"Price: ${tree['price']}")
            with col2:
                st.write(f"Height: {tree['height']}")
                st.write(f"Lifespan: {tree['lifespan']}")
            with col3:
                quantity = st.number_input(f"Quantity ({tree['name']})", min_value=1, step=1, key=f"qty_{tree['id']}")
            with col4:
                if st.button(f"Add to Cart ({tree['name']})", key=f"btn_{tree['id']}"):
                    self.add_to_cart(tree['id'], quantity)

    def add_to_cart(self, tree_id, quantity):
        tree = next((t for t in self.trees if t['id'] == tree_id), None)
        if tree:
            cart_item = {
                "name": tree["name"],
                "price": tree["price"],
                "quantity": quantity,
                "total": tree["price"] * quantity
            }
            st.session_state.cart.append(cart_item)
            st.success(f"Added {quantity} {tree['name']}(s) to cart!")

    def view_cart(self):
        if not st.session_state.cart:
            st.info("Your cart is empty!")
            return
        
        st.header("Shopping Cart")
        cart_df = pd.DataFrame(st.session_state.cart)
        st.dataframe(cart_df, hide_index=True)
        cart_total = sum(item['total'] for item in st.session_state.cart)
        st.write(f"Total Amount: ${cart_total}")

        if st.button("Proceed to Checkout"):
            self.create_razorpay_order(cart_total)

    def create_razorpay_order(self, amount):
        # Create Razorpay order
        order_amount = amount * 100  # Convert to paise
        order_currency = "INR"
        order_receipt = "receipt#1"
        notes = {"description": "Tree Shop Purchase"}
        
        try:
            order = self.razorpay_client.order.create(
                dict(amount=order_amount, currency=order_currency, receipt=order_receipt, notes=notes)
            )
            st.session_state.razorpay_payment = order
            self.display_payment_widget(order)
        except Exception as e:
            st.error(f"Error creating Razorpay order: {e}")

    def display_payment_widget(self, order):
        st.header("Complete Your Payment")
        st.markdown(
            f"""
            <script src="https://checkout.razorpay.com/v1/checkout.js"
            data-key="your_api_key"  <!-- Replace with your Razorpay API key -->
            data-amount="{order['amount']}" 
            data-currency="{order['currency']}" 
            data-order_id="{order['id']}" 
            data-buttontext="Pay Now" 
            data-name="Tree Shop"
            data-description="Purchase Trees"
            data-theme.color="#F37254"></script>
            """,
            unsafe_allow_html=True
        )

    def checkout(self):
        if st.session_state.razorpay_payment:
            st.success("Payment successfully completed!")
            st.session_state.cart = []  # Clear cart after payment
        else:
            st.warning("Please complete your payment!")

def main():
    st.title("Tree Shop")
    shop = TreeShop()

    menu = ["Display Available Trees", "View Cart"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Display Available Trees":
        shop.display_trees()

    elif choice == "View Cart":
        shop.view_cart()

if __name__ == "__main__":
    main()
