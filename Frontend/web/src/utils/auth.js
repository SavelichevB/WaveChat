import { apiSend } from "./api";

export const api_auth = {
    register: async (username, password) => {
       const res = await apiSend.post('auth/reg', {username, password})
       return res
    },

    login: async (username, password) => {
       const res = await apiSend.post('auth/login', {username, password})
       return res
    },

    logout: async () => {
       const res = await apiSend.post('auth/logout')
       return res
    },

    check: async () => {
       const res = await apiSend.get('auth/check')
       return res
    }
}