# DTCC Frontend

A modern, responsive frontend for the DTCC chat application built with React, TypeScript, and Material-UI.

## Features

- 🎨 Modern and professional UI design
- 🌙 Dark mode by default
- ✨ Smooth animations and transitions
- 🔒 Secure authentication system
- 💬 Real-time chat interface
- 📱 Fully responsive design
- 🚀 Fast and optimized performance

## Tech Stack

- React 18
- TypeScript
- Material-UI v5
- Framer Motion
- React Router v6
- Axios
- Vite

## Getting Started

### Prerequisites

- Node.js 16.x or later
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create a `.env` file in the root directory and add your environment variables:
```env
VITE_API_URL=http://localhost:3000
```

4. Start the development server:
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:5173`.

### Building for Production

To create a production build:

```bash
npm run build
# or
yarn build
```

The build artifacts will be stored in the `dist/` directory.

## Project Structure

```
src/
├── components/         # Reusable UI components
├── contexts/          # React contexts
├── theme.ts           # Material-UI theme configuration
├── App.tsx           # Main application component
└── main.tsx          # Application entry point
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
