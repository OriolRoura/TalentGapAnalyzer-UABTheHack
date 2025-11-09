import axios from 'axios';
import { API_SERVER, API_INITIAL } from "../utils/constants";

export const post = async (endpoint, data = null) => {
    // Eliminar barras iniciales del endpoint para evitar doble //
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    const fullPath = API_SERVER + API_INITIAL + cleanEndpoint;

    try {
        const response = await axios.post(fullPath, data);
        console.log("Response:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error posting data:", error);
        throw error; 
    }
};

export const get = async (endpoint) => {
    // Eliminar barras iniciales del endpoint para evitar doble //
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    const fullPath = API_SERVER + API_INITIAL + cleanEndpoint;

    try {
        const response = await axios.get(fullPath);
        console.log("Response:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error posting data:", error);
        throw error; 
    }
}