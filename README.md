# FoodBridge Project

## Description
Singapore generated over 755,000 tonnes of food waste in 2023—more than 10% of total national waste—while many citizens continue to face food insecurity. <br><br>
FoodBridge is a microservices platform that connects restaurants, volunteers, and food banks to address this crisis. By leveraging community center networks and geolocation services, the platform enables real-time coordination of food donations across the island.<br><br>
Foodbridge’s core goals:
<ul>
	<li>Simplify the process of donating non-perishables to encourage more donations</li>
	<li>Give volunteers the opportunity to give back to society in a new way</li>
	<li>Provides an avenue for food banks to receive food donations islandwide</li>
	
</ul>




## Prerequisites
IDE (Any) <br>
Node Package Manager <br>
Docker <br>

## Instructions
1. Insert `frontend.env` to the `/frontend` directory and `backend.env` in the main `/FoodBridge` directory
2. Rename both files back to `.env`
3. Clone the repo
4. Run `docker-compose -f docker-compose.yml -f docker-compose-amqp.yaml -f docker-compose-scenario1.yaml up --build -d` to start the docker containers
5. Navigate to the front-end with `cd frontend`
6. Start the frontend with `npm run`
7. Visit `localhost:3000` to access the UI.
8. Run `docker-compose -f docker-compose.yml -f docker-compose-amqp.yaml -f docker-compose-scenario1.yaml down -v` to remove docker containers


## Technical Architecture Diagram
![ESD_TechDiagram-Page-1](https://github.com/user-attachments/assets/65014e71-9437-47fd-a768-8e9787a314b5)


## Frameworks Utilized
### UI Stack
<div align="center">
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/vite.png" alt="Vite" title="Vite"/></code>
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/vue_js.png" alt="Vue.js" title="Vue.js"/></code>
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/tailwind_css.png" alt="Tailwind CSS" title="Tailwind CSS"/></code>
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/javascript.png" alt="JavaScript" title="JavaScript"/></code>
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/supabase.png" alt="Supabase" title="Supabase"/></code> <br>
  <i>Vite · Vue · Tailwind · JavaScript · Supabase</i>
</div>

### Microservices language
<div align="center">
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/javascript.png" alt="JavaScript" title="JavaScript"/></code>
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/python.png" alt="Python" title="Python"/></code>
  <br>
  <i>JavaScript · Python</i>
</div>

### Microservices Frameworks
<div align="center">
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/express.png" alt="Express" title="Express"/></code>
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/flask.png" alt="Flask" title="Flask"/></code>
  <br>
  <i>Express · Flask</i>
</div> 

### API Gateway
<div align="center">
  <img src="https://konghq.com/wp-content/uploads/2018/08/kong-combination-mark-color-256px.png" alt="Kong API Gateway" width="88"/> <br>
  <i>Kong</i>
</div>


### Storage Solutions
<div align="center">
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/supabase.png" alt="Supabase" title="Supabase"/></code><br>
  <i>Supabase</i>
</div>

### Message Brokers
<div align="center">
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/rabbitmq.png" alt="RabbitMQ" title="RabbitMQ"/></code><br>
  <i>RabbitMQ</i>
</div>

### Inter-service Communications
<div align="center">
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/grpc.png" alt="gRPC" title="gRPC"/></code>
	<code><img width="45" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/rest.png" alt="REST" title="REST"/></code><br>
  <i>gRPC · REST API</i>
</div>

### Other Technologies
<div align="center">
<img src="https://upload.wikimedia.org/wikipedia/commons/7/7e/Twilio-logo-red.svg" alt="Twilio" height="40"/>
<img src="https://upload.wikimedia.org/wikipedia/commons/4/4e/Docker_%28container_engine%29_logo.svg" alt="Docker" height="30"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg" alt="OpenAI" height="40"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/9/96/Socket-io.svg" alt="Socket.io" height="40"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/6/64/Logo-redis.svg" alt="Redis" height="40"/><br>
  <i>Twilio · Docker Compose · OpenAI · Socket.io · Redis</i>
</div>
<!-- ## UI
donor-ui
foodbank-ui
volunteer-ui

## Services
accountInfo
confirmDelivery
findVolunteers
locating
notifyVolunteers
productListing
productValidation
authentication
hub
notification
route



## Usage
- Frontend: Visit `localhost:3000` to access the UI.
- API Documentation: Available at `localhost:4000/docs`.

## Contributing
Feel free to fork and create a pull request! -->

## License
MIT License

