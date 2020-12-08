# muxy

RTMP-based streaming muxer for online events

Allows user to organize online self-streaming events, where each user can
stream herself to public channels or other streaming services.

## Install

The following is an `nginx-rtmp` sample configuration, that configures an RTMP
application to use Muxy allow/deny mechanism.

```
rtmp {
    application live {
        ...

        notify_update_timeout 10s;

        # HTTP callback when a stream starts publishing.
        # Returns 2xx only if publisher is allowed to publish now.
        on_publish http://localhost:4567/events/rtmp/on-publish/;

        # Called when a stream stops publishing.  Response is ignored.
        on_publish_done http://localhost:4567/events/rtmp/on-publish-done/;

        # Called with a period of notify_update_timeout,
        # to force disconnect publisher when her allotted time ends.
        on_update http://localhost:4567/events/rtmp/on-update/;
    }
}
```