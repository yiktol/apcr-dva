// Global variables
let currentPage = 1;
const itemsPerPage = 10;
let allOrders = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  // Initialize form submission
  const orderForm = document.getElementById('orderForm');
  orderForm.addEventListener('submit', handleFormSubmit);
  
  // Initialize order status refresh
  initOrderStatusRefresh();
  
  // Load initial orders
  loadOrders();
  
  // Initialize pagination
  document.getElementById('prevPage').addEventListener('click', () => changePage(-1));
  document.getElementById('nextPage').addEventListener('click', () => changePage(1));
  
  // Add refresh button to the card header instead of body
  const refreshButton = document.createElement('button');
  refreshButton.id = 'refreshOrders';
  refreshButton.className = 'btn btn-secondary refresh-button';
  refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
  refreshButton.addEventListener('click', handleRefreshOrders);
  
  // Insert refresh button in the card header next to the "Recent Orders" heading
  const ordersCardHeader = document.querySelector('.orders-table .card-header');
  ordersCardHeader.style.display = 'flex';
  ordersCardHeader.style.justifyContent = 'space-between';
  ordersCardHeader.style.alignItems = 'center';
  ordersCardHeader.appendChild(refreshButton);
});

// Handle refresh button click
async function handleRefreshOrders() {
  const refreshButton = document.getElementById('refreshOrders');
  
  // Disable button and show loading state
  refreshButton.disabled = true;
  refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
  
  try {
    await loadOrders();
    showNotification('Orders refreshed successfully!');
  } catch (error) {
    showNotification('Failed to refresh orders. Please try again.', 'error');
  } finally {
    // Re-enable button and restore original text
    refreshButton.disabled = false;
    refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
  }
}

// Load orders from server
async function loadOrders() {
  try {
    const response = await fetch('/sales');
    
    if (!response.ok) {
      throw new Error(`Orders request failed with status ${response.status}`);
    }
    
    const responseData = await response.json();
    
    // Extract orders array from the response object
    if (responseData.success && responseData.orders) {
      allOrders = responseData.orders;
    } else {
      allOrders = [];
      console.warn('No orders found in response or request was not successful');
    }
    
    // Sort orders by timestamp (most recent first)
    allOrders.sort((a, b) => {
      // Handle both string timestamps and numeric timestamps
      const timestampA = typeof a.timestamp === 'string' ? 
        new Date(a.timestamp).getTime() : 
        parseInt(a.timestamp);
      const timestampB = typeof b.timestamp === 'string' ? 
        new Date(b.timestamp).getTime() : 
        parseInt(b.timestamp);
      
      return timestampB - timestampA; // Most recent first
    });
    
    displayOrders();
    
  } catch (error) {
    console.error('Error fetching orders:', error);
    document.getElementById('ordersContainer').innerHTML = '<p class="error">Failed to load orders</p>';
    throw error; // Re-throw to handle in the calling function
  }
}

// Display orders with pagination
function displayOrders() {
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentOrders = allOrders.slice(startIndex, endIndex);
  
  const ordersContainer = document.getElementById('ordersContainer');
  
  // Create table
  let tableHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Customer</th>
          <th>Coffee</th>
          <th>Milk</th>
          <th>Size</th>
          <th>Qty</th>
          <th>Timestamp</th>
        </tr>
      </thead>
      <tbody>
  `;
  
  // Add table rows
  if (currentOrders.length === 0) {
    tableHTML += `
      <tr>
        <td colspan="7" class="no-orders">No orders found</td>
      </tr>
    `;
  } else {
    currentOrders.forEach(order => {
      // Format timestamp for display
      let formattedTimestamp = '-';
      if (order.timestamp) {
        try {
          // Handle both string timestamps (ISO format) and numeric timestamps
          const timestamp = typeof order.timestamp === 'string' ? 
            new Date(order.timestamp) : 
            new Date(parseInt(order.timestamp));
          
          if (!isNaN(timestamp.getTime())) {
            formattedTimestamp = timestamp.toLocaleString();
          }
        } catch (e) {
          console.warn('Invalid timestamp format:', order.timestamp);
        }
      }
      
      tableHTML += `
        <tr>
          <td>${order.salesid || '-'}</td>
          <td>${order.customer || '-'}</td>
          <td>${order.coffee || '-'}</td>
          <td>${order.milk || '-'}</td>
          <td>${order.size || '-'}</td>
          <td>${order.qty || '-'}</td>
          <td>${formattedTimestamp}</td>
        </tr>
      `;
    });
  }
  
  tableHTML += `
      </tbody>
    </table>
  `;
  
  ordersContainer.innerHTML = tableHTML;
  
  // Update pagination info
  updatePaginationInfo();
}

// Handle form submission
async function handleFormSubmit(event) {
  event.preventDefault();
  
  // Validate form
  if (!validateForm()) {
    return false;
  }
  
  try {
    const formData = new FormData(event.target);
    const orderData = {
      saleid: generateSaleId(),
      timestamp: Date.now(),
      customer: formData.get('CUSTOMER'),
      coffee: formData.get('COFFEE'),
      milk: formData.get('MILK'),
      size: formData.get('SIZE'),
      qty: formData.get('QTY')
    };
    
    await submitOrder(orderData);
    
    // Reset form and refresh data
    event.target.reset();
    await loadOrders();
    
    // Show success message
    showNotification('Order submitted successfully!');
    
  } catch (error) {
    console.error('Error submitting order:', error);
    showNotification('Failed to submit order. Please try again.', 'error');
  }
}

// Validate form data
function validateForm() {
  const nameInput = document.getElementById('customer');
  
  if (!nameInput.value.trim()) {
    showNotification('Name is required', 'error');
    nameInput.focus();
    return false;
  }
  
  return true;
}

// Generate a random sale ID
function generateSaleId() {
  return Math.random().toString(36).substring(2, 16);
}

// Submit order to server
async function submitOrder(orderData) {
 
  const response = await fetch('/cashier', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(orderData)
  });
  
  if (!response.ok) {
    throw new Error(`Server responded with ${response.status}`);
  }
  
  return await response.json();
}

// Initialize order status refresh countdown
function initOrderStatusRefresh() {
  let countdown = 3;
  const countdownElement = document.getElementById('countdown');
  
  // Get initial status
  getOrderStatus();
  
  // Set up countdown
  setInterval(() => {
    countdown--;
    
    if (countdown <= 0) {
      countdown = 3; // Reset to 3 seconds
      getOrderStatus();
    }
    
    countdownElement.textContent = countdown;
  }, 1000);
}

// Get order status from server
async function getOrderStatus() {
  try {
    const response = await fetch('/status');
    
    if (!response.ok) {
      throw new Error(`Status request failed with status ${response.status}`);
    }
    
    const statusData = await response.json();
    updateStatusDisplay(statusData);
    
  } catch (error) {
    console.error('Error fetching status:', error);
    document.getElementById('statusContainer').innerHTML = '<p class="error">Failed to load status</p>';
  }
}

// Update status display
function updateStatusDisplay(statusData) {
  const statusContainer = document.getElementById('statusContainer');
  
  statusContainer.innerHTML = `
    <table>
      <tr>
        <td>Barista (Lambda):</td>
        <td>${statusData.Queue1_MessagesInFlight}</td>
      </tr>
      <tr>
        <td>Cashier-Barista Queue (SQS):</td>
        <td>${statusData.Queue1_MessagesDelayed}</td>
      </tr>
      <tr>
        <td>Waiter (Lambda):</td>
        <td>${statusData.Queue2_MessagesInFlight}</td>
      </tr>
      <tr>
        <td>Sales (DynamoDB):</td>
        <td>${statusData.OrdersInDatabase}</td>
      </tr>
    </table>
  `;
}

// Change page
function changePage(delta) {
  const newPage = currentPage + delta;
  const totalPages = Math.ceil(allOrders.length / itemsPerPage);
  
  if (newPage >= 1 && newPage <= totalPages) {
    currentPage = newPage;
    displayOrders();
  }
}

// Update pagination info
function updatePaginationInfo() {
  const totalPages = Math.max(1, Math.ceil(allOrders.length / itemsPerPage));
  document.getElementById('pageInfo').textContent = `Page ${currentPage} of ${totalPages}`;
  
  // Enable/disable pagination buttons
  document.getElementById('prevPage').disabled = currentPage === 1;
  document.getElementById('nextPage').disabled = currentPage === totalPages || allOrders.length === 0;
}

// Show notification
function showNotification(message, type = 'success') {
  // Create notification container if it doesn't exist
  let notificationContainer = document.getElementById('notificationContainer');
  if (!notificationContainer) {
    notificationContainer = document.createElement('div');
    notificationContainer.id = 'notificationContainer';
    notificationContainer.className = 'notification-container';
    document.body.insertBefore(notificationContainer, document.body.firstChild);
  }
  
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;
  
  notificationContainer.appendChild(notification);
  
  // Remove notification after 3 seconds
  setTimeout(() => {
    notification.classList.add('fade-out');
    setTimeout(() => {
      notification.remove();
      
      // Remove container if empty
      if (notificationContainer.children.length === 0) {
        notificationContainer.remove();
      }
    }, 500);
  }, 3000);
}
