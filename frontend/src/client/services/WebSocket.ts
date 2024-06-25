const WS_URL = import.meta.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

let websocket: WebSocket;

const connect = (user_id: number | undefined): WebSocket => {
    websocket = new WebSocket(`${WS_URL}/${user_id}`);

    websocket.onopen = () => {
        console.log('WebSocket connection established');
    };

    websocket.onerror = (error) => {
        console.error('WebSocket error', error);
    };

    websocket.onclose = (event) => {
        console.log('WebSocket connection closed', event);
        // Attempt to reconnect after a delay
        setTimeout(() => connect(user_id), 1000);
    };

    return websocket;
};

const disconnect = () => {
    if (websocket) {
        websocket.close();
    }
};

export default {
    connect,
    disconnect
};
