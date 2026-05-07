import { useState, useEffect, useRef, useCallback } from "react"
import { io } from 'socket.io-client'

export function useSocket(userId) {
    const socket = useRef(null)
    const [ isConnected, setIsConnected ] = useState(false)
    const [ isReady, setIsReady ] = useState(false) 

    useEffect(() => {
        if(!userId) return

        socket.current = io('http://localhost:3333', {
            withCredentials: true,
            transports: ['websocket']
        })

        socket.current.on('connect', () => {
             console.log('WS-connected-WaveChat')
             setIsConnected(true)
             setIsReady(true)
             socket.current.emit('join', {})
        })

        socket.current.on('disconnect', () => {
            console.log('WS-dissconnected-WaveChat')
            setIsConnected(false)
            setIsReady(false)
        })

        return () => {
            if (socket.current) {
                socket.current.disconnect()
                socket.current = null
                setIsReady(false)
            }
        }
    }, [userId])

    // Send/get message - web socket : 

    const sendMessage = useCallback((chatId, toId, text, tempId) => {
        if(socket.current && isConnected) {
            socket.current.emit('send_message', {
                chat_id: chatId,
                to_id: toId,
                text: text,
                temp_id: tempId
            })
            return true
        }
        return false
    }, [isConnected])

    const onMessage = useCallback((callback) => {
        if(socket.current && isReady) { 
           socket.current.on('ws_message', callback)
           return () => { 
            if(socket.current) socket.current.off('ws_message', callback)
           }
        }
        return () => {}
    }, [isReady])

    const onLog = useCallback((callback) => {
        if (socket.current && isReady) {
            socket.current.on('ws_log', callback)
            return () => { 
             if(socket.current) socket.current.off('ws_log', callback)
            }
        }
        return () => {}
    }, [isReady])

    const onError = useCallback((callback) => {
        if (socket.current && isReady) {
            socket.current.on('ws_error', callback)
            return () => {
               if(socket.current) socket.current.off('ws_error', callback)
            }
        }
        return () => {}
    }, [isReady])

    // Delete message - web socket : 

    const delMessage = useCallback((message_id) => {
        if(socket.current && isConnected) {
            socket.current.emit('del_message', {
                message_id: message_id
            })
            return true
        }
        return false
    }, [isConnected])

    const onDelMessage = useCallback((callback) => {
        if(socket.current && isReady) {
            socket.current.on('ws_del_message', callback)
            return () => {
                if(socket.current) socket.current.off('ws_del_message', callback)
            }
        }
        return () => {}
    }, [isReady])

    const onDelLog = useCallback((callback) => {
        if(socket.current && isReady) {
            socket.current.on('ws_del_log', callback)
            return () => {
                if(socket.current) socket.current.off('ws_del_log', callback)
            }
        }
        return () => {}
    }, [isReady])

    const onDelError = useCallback((callback) => {
        if(socket.current && isReady) {
           socket.current.on('ws_del_error', callback)
           return () => {
            if(socket.current) socket.current.off('ws_del_error', callback)
           }
        }
        return () => {}
    }, [isReady])

    // Read message - web socket: 

    const readMessage = useCallback((chat_id) => {
         if(socket.current && isConnected) {
            socket.current.emit('read_message', {
                chat_id: chat_id
            })
            return true            
         }
         return false
    }, [isConnected])

    const onReadMessage = useCallback((callback) => {
        if(socket.current && isReady) {
            socket.current.on('ws_chat_read', callback)
            return () => {
                if(socket.current) socket.current.off('ws_chat_read', callback)
            }
        }
        return () => {}
    }, [isReady])

    return {
      isConnected,
      isReady,
      sendMessage,
      onMessage,
      onLog,
      onError,
      delMessage,
      onDelMessage,
      onDelLog,
      onDelError,
      readMessage,
      onReadMessage
    }
}