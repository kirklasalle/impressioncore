import React from 'react';
import ReactDOM from 'react-dom';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import App from './App';
import './index.css';

// Extend the theme to include custom colors, fonts, etc.
const theme = extendTheme({
    colors: {
        brand: {
            50: '#e6f7ff',
            100: '#b3e0ff',
            200: '#80caff',
            300: '#4db3ff',
            400: '#1a9dff',
            500: '#0080e6',
            600: '#0066b3',
            700: '#004d80',
            800: '#00334d',
            900: '#001a26',
        },
    },
    fonts: {
        body: 'Inter, system-ui, sans-serif',
        heading: 'Inter, system-ui, sans-serif',
    },
});

ReactDOM.render(
    <React.StrictMode>
        <ChakraProvider theme={theme}>
            <App />
        </ChakraProvider>
    </React.StrictMode>,
    document.getElementById('root')
);
