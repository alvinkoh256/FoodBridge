import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'FoodBridge Product Listing API',
      version: '1.0.0',
      description: 'API for managing product listings in the FoodBridge application',
      contact: {
        name: 'FoodBridge Team'
      },
    },
    servers: [
      {
        url: 'http://localhost:5005',
        description: 'Development server',
      },
    ],
  },
  apis: ['./app.js', './server.js'], // Path to the API docs
};

const specs = swaggerJsdoc(options);

export { swaggerUi, specs };