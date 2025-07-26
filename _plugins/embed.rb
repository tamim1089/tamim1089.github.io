module Jekyll
  class EmbedTag < Liquid::Tag
    def initialize(tag_name, text, tokens)
      super
      @url = text.strip.match(/url=["'](.+?)["']/)[1]
    end

    def render(context)
      <<~HTML
      <iframe width="560" height="315" src="#{@url.sub('watch?v=', 'embed/')}" 
              frameborder="0" allowfullscreen></iframe>
      HTML
    end
  end
end

Liquid::Template.register_tag('embed', Jekyll::EmbedTag)
