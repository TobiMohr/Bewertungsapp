// src/async-sessions/adapters/reviewAdapter.js
export function buildChannelReviews(
    messages,
    messageCriteria,
    criterias,
    cfg = {
        msgId: 'id',
        msgChannel: 'channel_id',
        msgChannelName: 'channel',
        msgCreated: 'sent_at',
        mcMsgId: 'message_id',
        mcCritId: 'criterion_id',
        mcCount: 'count_value',
        mcBool: 'is_fulfilled',
        mcText: 'text_value',
        critId: 'id',
        critName: 'name',
    },
    normalizeCount01 = true,
    users = [] // optional
) {
    const userById = new Map(users.map(u => [u.id, u]));
    const critById  = new Map(criterias.map(c => [c[cfg.critId], c]));

    // Messages je Channel
    const msgsByChannel = new Map();
    for (const m of messages) {
        const ch = m[cfg.msgChannel];
        if (!msgsByChannel.has(ch)) msgsByChannel.set(ch, []);
        msgsByChannel.get(ch).push(m);
    }

    // MC je Message
    const mcByMsg = new Map();
    for (const mc of messageCriteria) {
        const mid = mc[cfg.mcMsgId];
        if (!mcByMsg.has(mid)) mcByMsg.set(mid, []);
        mcByMsg.get(mid).push(mc);
    }

    // Aggregate je Channel
    const rows = [];
    for (const [channelId, msgs] of msgsByChannel.entries()) {
        // Kriterium -> Evidenzliste + Score
        const critAgg = new Map();

        for (const m of msgs) {
            const mids = m[cfg.msgId];
            const user = userById.get(m.user_id);
            const mcList = mcByMsg.get(mids) || [];

            for (const mc of mcList) {
                const cid   = mc[cfg.mcCritId];
                const count = mc[cfg.mcCount];       // 0/1
                const bool  = mc[cfg.mcBool];
                const text  = mc[cfg.mcText];

                if (!critAgg.has(cid)) {
                    const c = critById.get(cid);
                    critAgg.set(cid, {
                        criterionId: cid,
                        criterionName: c ? c[cfg.critName] : String(cid),
                        scoreRaw: 0,
                        evidence: []
                    });
                }
                const bucket = critAgg.get(cid);

                // Evidenz aufnehmen, wenn "positiv" (z. B. count 1 / bool true / text vorhanden)
                const isPositive = (count && Number(count) > 0) || (bool === true) || (text && String(text).trim().length > 0);
                if (isPositive) {
                    bucket.evidence.push({
                        messageId: m[cfg.msgId],
                        content: m.content,
                        username: user?.username ?? null,
                        userId: m.user_id ?? null,
                        sentAt: m[cfg.msgCreated] ?? null,
                        countValue: count ?? null,
                        isFulfilled: bool ?? null,
                        textValue: text ?? null,
                    });
                }

                // Scorebildung: einfache 0/1 -> 0/100
                if (normalizeCount01) {
                    bucket.scoreRaw += (Number(count) ? 100 : 0);
                } else {
                    bucket.scoreRaw += Number(count || 0);
                }
            }
        }

        // In Breakdown umwandeln
        const breakdown = Array.from(critAgg.values()).map(x => ({
            criterionId: x.criterionId,
            criterionName: x.criterionName,
            score: Math.max(0, Math.min(100, Math.round(x.scoreRaw / Math.max(1, msgs.length)))),
            evidence: x.evidence
        }));

        rows.push({
            id: channelId,                        // "Session" = Channel
            channelId,
            channelName: msgs[0]?.[cfg.msgChannelName] ?? String(channelId),
            createdAt: msgs[0]?.[cfg.msgCreated] ?? null,
            updatedAt: msgs[msgs.length - 1]?.[cfg.msgCreated] ?? null,
            status: 'DONE',
            approved: true,                       // Mock
            summaryText: `Aggregiertes Feedback für #${msgs[0]?.[cfg.msgChannelName] ?? channelId}`,
            aggregateScore: breakdown.length
                ? Math.round(breakdown.reduce((a,b)=>a+b.score,0)/breakdown.length)
                : null,
            _editedBreakdown: breakdown,
            _dirty: false,
        });
    }

    return rows;
}
