import { ref, onBeforeUnmount } from "vue";

export function usePolling(fn, interval = 5000) {
    const timer = ref(null);
    const running = ref(false);

    const start = async () => {
        running.value = true;
        await fn();
        timer.value = setInterval(fn, interval);
    };
    const stop = () => {
        running.value = false;
        if (timer.value) clearInterval(timer.value);
    };

    onBeforeUnmount(stop);
    return { start, stop, running };
}
