document.addEventListener('DOMContentLoaded', function() {
    // Extract product ID from the data attribute
    var productId = document.querySelector('#product-info').getAttribute('data-product-id');
  
    // Function to reconnect a WebSocket
    function reconnectWebSocket(socket, url) {
      console.log(`Attempting to reconnect to ${url}`);
      socket.close(); // Close the existing socket (if any)
      socket = new WebSocket(url); // Create a new WebSocket connection
    }
  
    // WebSocket for bids with reconnection logic
    var bidSocket = new WebSocket(`ws://${window.location.host}/ws/bid/${productId}/`);
  
    bidSocket.onmessage = function(e) {
      var data = JSON.parse(e.data);
      var bid = data.bid;
      console.log('New bid received:', bid);
      // Update the UI with the new bid - Implement this as per your UI requirements
    };
  
    bidSocket.onclose = function(e) {
      console.error('Bid socket closed unexpectedly');
      // Attempt to reconnect after a delay
      setTimeout(function() {
        reconnectWebSocket(bidSocket, `ws://${window.location.host}/ws/bid/${productId}/`);
      }, 5000); // Reconnect after 5 seconds
    };
  
    // Example of sending a bid
    document.querySelector('#placeBid').addEventListener('click', function() {
      var bidAmount = document.querySelector('#bidAmount').value;
      bidSocket.send(JSON.stringify({
        'bid': bidAmount
      }));
    });
  
    // WebSocket for notifications with reconnection logic
    var notificationSocket = new WebSocket(`ws://${window.location.host}/ws/notifications/`);
  
    notificationSocket.onmessage = function(e) {
      var data = JSON.parse(e.data);
      var notification = data.notification;
      console.log('New notification:', notification);
    
      // Display the notification to the user
      var notificationList = document.querySelector('#notification-list');
      var newItem = document.createElement('div');
      newItem.classList.add('list-group-item');
      newItem.textContent = notification;
      notificationList.appendChild(newItem);
    };
  
    notificationSocket.onclose = function(e) {
      console.error('Notification socket closed unexpectedly');
      // Attempt to reconnect after a delay
      setTimeout(function() {
        reconnectWebSocket(notificationSocket, `ws://${window.location.host}/ws/notifications/`);
      }, 5000); // Reconnect after 5 seconds
    };
  
    // Toggle notification dropdown - Implement this as per your actual implementation
    document.getElementById('notification-icon').addEventListener('click', function() {
      document.getElementById('notification-dropdown').classList.toggle('show'); // Assuming dropdown uses 'show' class for visibility
    });
  });