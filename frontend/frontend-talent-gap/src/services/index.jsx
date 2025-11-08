import axios from 'axios';
import { API_SERVER, API_INITIAL } from "../utils/constants";

export const post = async (endpoint, data = null) => {
    const fullPath = API_SERVER + API_INITIAL + endpoint;

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
    const fullPath = API_SERVER + API_INITIAL + endpoint;

    try {
        const response = await axios.get(fullPath);
        console.log("Response:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error posting data:", error);
        throw error; 
    }
}