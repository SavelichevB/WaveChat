import { useState, useEffect, useRef, useCallback } from "react"

export function useSocket(userId) {
    const ws = useRef(null)
    const [ isConnected, setIsConnected ] = useState(false)
    const [ isReady, setIsReady ] = useState(false)
    const listeners = useRef({})
    const userIdRef = useRef(userId)

    useEffect(() => {
        userIdRef.current = userId
    }, [userId])

    useEffect(() => {
        if(!userId) return

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = `${protocol}//${window.location.host}/ws`

        ws.current = new WebSocket(wsUrl)

        ws.current.onopen = () => {
             console.log('WS-connected-WaveChat')
             setIsConnected(true)
             setIsReady(true)
             ws.current.send(JSON.stringify({ type: 'join' }))
        }

        ws.current.onclose = () => {
            console.log('WS-disconnected-WaveChat')
            setIsConnected(false)
            setIsReady(false)
        }

        ws.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                const type = data.type
                const handlers = listeners.current[type] || []
                handlers.forEach(cb => {
                    try { cb(data) } catch(e) { console.error('WS handler error:', e) }
                })
            } catch(e) {
                console.error('WS parse error:', e)
            }
        }

        return () => {
            if (ws.current) {
                ws.current.close()
                ws.current = null
                setIsReady(false)
                setIsConnected(false)
            }
        }
    }, [userId])

    const addListener = useCallback((event, callback) => {
        if (!listeners.current[event]) {
            listeners.current[event] = []
        }
        listeners.current[event].push(callback)
        return () => {
            if (listeners.current[event]) {
                listeners.current[event] = listeners.current[event].filter(cb => cb !== callback)
            }
        }
    }, [])

    const sendMessage = useCallback((chatId, toId, text, tempId) => {
        if(ws.current && isConnected) {
            ws.current.send(JSON.stringify({
                type: 'send_message',
                chat_id: chatId,
                to_id: toId,
                text: text,
                temp_id: tempId
            }))
            return true
        }
        return false
    }, [isConnected])

    const onMessage = useCallback((callback) => {
        return addListener('ws_message', callback)
    }, [addListener])

    const onLog = useCallback((callback) => {
        return addListener('ws_log', callback)
    }, [addListener])

    const onError = useCallback((callback) => {
        return addListener('ws_error', callback)
    }, [addListener])

    const delMessage = useCallback((message_id) => {
        if(ws.current && isConnected) {
            ws.current.send(JSON.stringify({
                type: 'del_message',
                message_id: message_id
            }))
            return true
        }
        return false
    }, [isConnected])

    const onDelMessage = useCallback((callback) => {
        return addListener('ws_del_message', callback)
    }, [addListener])

    const onDelLog = useCallback((callback) => {
        return addListener('ws_del_log', callback)
    }, [addListener])

    const onDelError = useCallback((callback) => {
        return addListener('ws_del_error', callback)
    }, [addListener])

    const readMessage = useCallback((chat_id) => {
         if(ws.current && isConnected) {
            ws.current.send(JSON.stringify({
                type: 'read_message',
                chat_id: chat_id
            }))
            return true            
         }
         return false
    }, [isConnected])

    const onReadMessage = useCallback((callback) => {
        return addListener('ws_chat_read', callback)
    }, [addListener])

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
