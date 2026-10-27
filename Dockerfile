FROM ruby:4-alpine

RUN apk add --no-cache build-base git libcurl linux-headers openssl-dev tzdata \
    && git config --global --add safe.directory /app

WORKDIR /app

ENV BUNDLE_APP_CONFIG=/usr/local/bundle/config \
    BUNDLE_PATH=/usr/local/bundle

COPY Gemfile Gemfile.lock* ./
RUN bundle install

EXPOSE 4001 35730

ENTRYPOINT ["sh", "-c", "(bundle check || bundle install) && exec \"$@\"", "--"]
CMD ["bundle", "exec", "jekyll", "serve", "--host", "0.0.0.0", "--port", "4001", "--livereload", "--livereload-port", "35730"]
